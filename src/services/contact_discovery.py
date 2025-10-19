"""Contact discovery service with validation and error handling."""

import logging
from typing import List, Optional
from datetime import datetime

from src.models.job_posting import JobPosting
from src.models.search_result import SearchResult
from src.models.batch_job import BatchJob
from src.models import BatchStatus
from src.agent.runtime import AgentRuntime
from src.agent.orchestrator import process_batch_job as orchestrate_batch

logger = logging.getLogger(__name__)


class ContactDiscoveryService:
    """
    High-level service for HR contact discovery.

    Provides validation, error handling, and business logic around
    the core agent runtime.
    """

    def __init__(self, agent_runtime: Optional[AgentRuntime] = None):
        """
        Initialize contact discovery service.

        Args:
            agent_runtime: Optional AgentRuntime instance
        """
        self.agent_runtime = agent_runtime or AgentRuntime()
        logger.info("Initialized ContactDiscoveryService")

    def discover_single_contact(self, job_posting: JobPosting) -> SearchResult:
        """
        Discover HR contact for a single job posting.

        Args:
            job_posting: Job posting to search for

        Returns:
            SearchResult with contact information

        Raises:
            ValueError: If job posting is invalid
        """
        # Validate job posting
        self._validate_job_posting(job_posting)

        logger.info(
            f"Starting contact discovery for {job_posting.company_name} - {job_posting.job_title}"
        )

        # Perform discovery
        result = self.agent_runtime.discover_contact(job_posting)

        # Log outcome
        if result.hr_contact:
            logger.info(
                f"Successfully discovered contact: {result.hr_contact.name} "
                f"(confidence: {result.hr_contact.confidence_score:.2f})"
            )
        else:
            logger.warning(f"No contact found for {job_posting.company_name}")

        return result

    def discover_batch_contacts(
        self, job_postings: List[JobPosting]
    ) -> BatchJob:
        """
        Discover HR contacts for multiple job postings.

        Args:
            job_postings: List of job postings to process

        Returns:
            BatchJob with results for all postings

        Raises:
            ValueError: If batch is invalid (empty or too large)
        """
        # Validate batch
        if not job_postings:
            raise ValueError("Batch must contain at least one job posting")

        if len(job_postings) > 50:
            raise ValueError("Batch size limited to 50 job postings")

        # Validate each posting
        for idx, posting in enumerate(job_postings):
            try:
                self._validate_job_posting(posting)
            except ValueError as e:
                raise ValueError(f"Invalid job posting at index {idx}: {str(e)}")

        logger.info(f"Starting batch discovery for {len(job_postings)} job postings")

        # Create batch job
        batch_job = BatchJob(job_postings=job_postings)

        # Process batch
        batch_job = orchestrate_batch(batch_job, self.agent_runtime)

        # Log summary
        logger.info(
            f"Batch completed with status {batch_job.status.value}. "
            f"Successful: {len(batch_job.results) - batch_job.error_count}/{len(batch_job.results)}"
        )

        return batch_job

    def _validate_job_posting(self, job_posting: JobPosting) -> None:
        """
        Validate a job posting.

        Args:
            job_posting: Job posting to validate

        Raises:
            ValueError: If job posting is invalid
        """
        # Check company name
        if not job_posting.company_name or not job_posting.company_name.strip():
            raise ValueError("Company name is required")

        # Check job title
        if not job_posting.job_title or not job_posting.job_title.strip():
            raise ValueError("Job title is required")

        # Warn if no description provided (reduces accuracy)
        if not job_posting.description:
            logger.debug(
                f"Job posting for {job_posting.company_name} has no description. "
                "This may reduce contact discovery accuracy."
            )

    def get_discovery_statistics(self, batch_job: BatchJob) -> dict:
        """
        Calculate statistics for a completed batch job.

        Args:
            batch_job: Completed batch job

        Returns:
            Dictionary with statistics
        """
        total = len(batch_job.results)
        successful = total - batch_job.error_count

        # Count by source
        source_counts = {}
        for result in batch_job.results:
            if result.hr_contact:
                source = result.hr_contact.source.value
                source_counts[source] = source_counts.get(source, 0) + 1

        # Calculate average confidence
        confidences = [
            result.hr_contact.confidence_score
            for result in batch_job.results
            if result.hr_contact
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Calculate average duration
        durations = [result.search_duration_seconds for result in batch_job.results]
        avg_duration = sum(durations) / len(durations) if durations else 0.0

        return {
            "total_jobs": total,
            "successful": successful,
            "failed": batch_job.error_count,
            "success_rate": successful / total if total > 0 else 0.0,
            "sources": source_counts,
            "average_confidence": avg_confidence,
            "average_duration_seconds": avg_duration,
            "total_duration_seconds": sum(durations),
        }
