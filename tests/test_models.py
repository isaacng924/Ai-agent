"""Test data models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models.job_posting import JobPosting
from src.models.hr_contact import HRContact
from src.models.search_result import SearchResult
from src.models.batch_job import BatchJob
from src.models import ContactSource, BatchStatus


class TestJobPosting:
    """Test JobPosting model."""

    def test_create_valid_job_posting(self):
        """Test creating a valid job posting."""
        job = JobPosting(
            company_name="Anthropic",
            job_title="AI Researcher",
            description="Work on AI safety",
            job_url="https://anthropic.com/careers",
        )

        assert job.company_name == "Anthropic"
        assert job.job_title == "AI Researcher"
        assert job.description == "Work on AI safety"

    def test_job_posting_minimal(self):
        """Test creating job posting with only required fields."""
        job = JobPosting(
            company_name="OpenAI",
            job_title="Software Engineer",
        )

        assert job.company_name == "OpenAI"
        assert job.job_title == "Software Engineer"
        assert job.description is None
        assert job.job_url is None

    def test_job_posting_validation_errors(self):
        """Test validation errors for invalid data."""
        # Missing required fields
        with pytest.raises(ValidationError):
            JobPosting(company_name="Test")

        # Empty strings
        with pytest.raises(ValidationError):
            JobPosting(company_name="", job_title="Engineer")

        with pytest.raises(ValidationError):
            JobPosting(company_name="Test", job_title="")


class TestHRContact:
    """Test HRContact model."""

    def test_create_valid_hr_contact(self):
        """Test creating a valid HR contact."""
        contact = HRContact(
            name="Jane Smith",
            role="Technical Recruiter",
            company="Anthropic",
            profile_url="https://linkedin.com/in/janesmith",
            source=ContactSource.LINKEDIN,
            confidence_score=0.95,
        )

        assert contact.name == "Jane Smith"
        assert contact.role == "Technical Recruiter"
        assert contact.confidence_score == 0.95
        assert contact.source == ContactSource.LINKEDIN

    def test_hr_contact_confidence_validation(self):
        """Test confidence score validation."""
        # Valid confidence scores
        contact = HRContact(
            name="Test",
            role="Recruiter",
            company="Test Co",
            source=ContactSource.LINKEDIN,
            confidence_score=0.0,
        )
        assert contact.confidence_score == 0.0

        contact = HRContact(
            name="Test",
            role="Recruiter",
            company="Test Co",
            source=ContactSource.LINKEDIN,
            confidence_score=1.0,
        )
        assert contact.confidence_score == 1.0

        # Invalid confidence scores
        with pytest.raises(ValidationError):
            HRContact(
                name="Test",
                role="Recruiter",
                company="Test Co",
                source=ContactSource.LINKEDIN,
                confidence_score=-0.1,
            )

        with pytest.raises(ValidationError):
            HRContact(
                name="Test",
                role="Recruiter",
                company="Test Co",
                source=ContactSource.LINKEDIN,
                confidence_score=1.1,
            )


class TestSearchResult:
    """Test SearchResult model."""

    def test_create_search_result_with_contact(self):
        """Test creating a search result with a contact found."""
        job = JobPosting(company_name="Test Co", job_title="Engineer")
        contact = HRContact(
            name="John Doe",
            role="Recruiter",
            company="Test Co",
            source=ContactSource.WEB_SEARCH,
            confidence_score=0.8,
        )

        result = SearchResult(
            job_posting=job,
            hr_contact=contact,
            reasoning="Found via LinkedIn search",
            search_duration_seconds=5.2,
        )

        assert result.job_posting == job
        assert result.hr_contact == contact
        assert result.reasoning == "Found via LinkedIn search"
        assert result.search_duration_seconds == 5.2
        assert isinstance(result.timestamp, datetime)
        assert result.error_message is None

    def test_create_search_result_without_contact(self):
        """Test creating a search result when no contact found."""
        job = JobPosting(company_name="Test Co", job_title="Engineer")

        result = SearchResult(
            job_posting=job,
            hr_contact=None,
            reasoning="No suitable contacts found",
            search_duration_seconds=3.0,
            suggestions=["Check company website", "Try LinkedIn directly"],
        )

        assert result.hr_contact is None
        assert len(result.suggestions) == 2


class TestBatchJob:
    """Test BatchJob model."""

    def test_create_batch_job(self):
        """Test creating a batch job."""
        jobs = [
            JobPosting(company_name="Company A", job_title="Engineer"),
            JobPosting(company_name="Company B", job_title="Designer"),
        ]

        batch = BatchJob(job_postings=jobs)

        assert len(batch.job_postings) == 2
        assert batch.status == BatchStatus.PENDING
        assert batch.progress == 0
        assert batch.error_count == 0
        assert len(batch.results) == 0
        assert isinstance(batch.id, str)
        assert isinstance(batch.created_at, datetime)

    def test_batch_job_validation(self):
        """Test batch job validation."""
        # Empty batch
        with pytest.raises(ValidationError):
            BatchJob(job_postings=[])

        # Too many jobs (max 50)
        jobs = [
            JobPosting(company_name=f"Company {i}", job_title="Engineer")
            for i in range(51)
        ]
        with pytest.raises(ValidationError):
            BatchJob(job_postings=jobs)
