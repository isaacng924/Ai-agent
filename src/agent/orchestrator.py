"""Orchestration logic for batch job processing."""

import logging
import time
from typing import List, Callable, Optional
from datetime import datetime, timezone

from src.models.batch_job import BatchJob
from src.models.job_posting import JobPosting
from src.models.search_result import SearchResult
from src.models import BatchStatus
from src.agent.runtime import AgentRuntime

logger = logging.getLogger(__name__)


def process_batch_job(
    batch_job: BatchJob,
    agent_runtime: AgentRuntime = None,
    progress_callback: Optional[Callable[[int, int, SearchResult], None]] = None,
) -> BatchJob:
    """
    Process a batch job by discovering HR contacts for all job postings.

    Args:
        batch_job: BatchJob to process
        agent_runtime: Optional AgentRuntime instance (creates new if not provided)
        progress_callback: Optional callback function(current, total, result) for progress updates

    Returns:
        Updated BatchJob with results and status
    """
    if agent_runtime is None:
        agent_runtime = AgentRuntime()

    logger.info(
        f"Starting batch job {batch_job.id} with {len(batch_job.job_postings)} job postings"
    )

    # Update status to IN_PROGRESS
    batch_job.status = BatchStatus.IN_PROGRESS
    batch_job.started_at = datetime.now(timezone.utc)
    batch_job.progress = 0
    batch_job.error_count = 0

    results: List[SearchResult] = []

    # Process each job posting
    for idx, job_posting in enumerate(batch_job.job_postings):
        try:
            logger.info(
                f"Processing job {idx + 1}/{len(batch_job.job_postings)}: "
                f"{job_posting.company_name} - {job_posting.job_title}"
            )

            # Discover contact for this job posting
            result = agent_runtime.discover_contact(
                job_posting=job_posting,
                session_id=f"{batch_job.id}-{idx}",
            )

            results.append(result)

            # Update progress
            batch_job.progress = idx + 1

            # Track errors
            if result.error_message:
                batch_job.error_count += 1

            logger.info(
                f"Completed job {idx + 1}/{len(batch_job.job_postings)} - "
                f"Contact: {result.hr_contact.name if result.hr_contact else 'None'}"
            )

            # Call progress callback if provided
            if progress_callback:
                progress_callback(idx + 1, len(batch_job.job_postings), result)

            # Add delay between requests to avoid rate limiting (except for last job)
            if idx < len(batch_job.job_postings) - 1:
                time.sleep(2)  # 2 second delay between jobs

        except Exception as e:
            logger.error(
                f"Failed to process job posting {job_posting.company_name} - "
                f"{job_posting.job_title}: {str(e)}",
                exc_info=True,
            )

            # Create failed result
            failed_result = SearchResult(
                job_posting=job_posting,
                hr_contact=None,
                reasoning="Processing failed due to unexpected error",
                search_duration_seconds=0.0,
                timestamp=datetime.now(timezone.utc),
                error_message=str(e),
            )
            results.append(failed_result)

            batch_job.progress = idx + 1
            batch_job.error_count += 1

            # Call progress callback for failed jobs too
            if progress_callback:
                progress_callback(idx + 1, len(batch_job.job_postings), failed_result)

    # Update batch job with results
    batch_job.results = results
    batch_job.completed_at = datetime.now(timezone.utc)

    # Determine final status
    if batch_job.error_count == 0:
        batch_job.status = BatchStatus.COMPLETED
    elif batch_job.error_count == len(batch_job.job_postings):
        batch_job.status = BatchStatus.FAILED
    else:
        batch_job.status = BatchStatus.PARTIALLY_COMPLETED

    logger.info(
        f"Batch job {batch_job.id} completed with status {batch_job.status.value}. "
        f"Successful: {len(results) - batch_job.error_count}/{len(results)}"
    )

    return batch_job


def process_single_job(job_posting: JobPosting, agent_runtime: AgentRuntime = None) -> SearchResult:
    """
    Process a single job posting (convenience function).

    Args:
        job_posting: Job posting to process
        agent_runtime: Optional AgentRuntime instance

    Returns:
        SearchResult for the job posting
    """
    if agent_runtime is None:
        agent_runtime = AgentRuntime()

    logger.info(
        f"Processing single job: {job_posting.company_name} - {job_posting.job_title}"
    )

    return agent_runtime.discover_contact(job_posting)
