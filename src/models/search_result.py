"""SearchResult data model."""

from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
from src.models.job_posting import JobPosting
from src.models.hr_contact import HRContact


class SearchResult(BaseModel):
    """Result of HR contact discovery for a job posting."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_posting": {
                    "company_name": "Anthropic",
                    "job_title": "AI Safety Researcher",
                },
                "hr_contact": {
                    "name": "Jane Smith",
                    "role": "Engineering Recruiter",
                    "company": "Anthropic",
                    "profile_url": "https://linkedin.com/in/janesmith",
                    "source": "linkedin",
                    "confidence_score": 0.9,
                },
                "reasoning": "Jane Smith is Anthropic's Engineering Recruiter with a focus on AI research roles. Her LinkedIn shows recent posts about hiring for the safety team.",
                "search_duration_seconds": 12.5,
                "timestamp": "2025-10-12T14:30:00Z",
            }
        }
    )

    job_posting: JobPosting = Field(
        ...,
        description="The original job posting that was searched",
    )

    hr_contact: Optional[HRContact] = Field(
        None,
        description="Discovered HR contact (None if not found)",
    )

    reasoning: str = Field(
        ...,
        description="Explanation of why this contact was selected (or why none found)",
        min_length=10,
        max_length=3000,
    )

    search_duration_seconds: float = Field(
        ...,
        description="Time taken for contact discovery",
        ge=0.0,
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this search was performed (UTC)",
    )

    error_message: Optional[str] = Field(
        None,
        description="Error message if search failed",
    )

    suggestions: Optional[list[str]] = Field(
        None,
        description="Suggestions for user if no contact found",
    )
