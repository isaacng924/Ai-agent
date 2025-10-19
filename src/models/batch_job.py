"""BatchJob data model."""

from typing import List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field, ConfigDict
from src.models import BatchStatus
from src.models.job_posting import JobPosting
from src.models.search_result import SearchResult


class BatchJob(BaseModel):
    """A batch of job postings for HR contact discovery."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "job_postings": [
                    {"company_name": "Anthropic", "job_title": "AI Safety Researcher"},
                    {"company_name": "TechCorp", "job_title": "Senior Engineer"},
                ],
                "status": "in_progress",
                "results": [],
                "created_at": "2025-10-12T14:00:00Z",
                "started_at": "2025-10-12T14:00:05Z",
                "completed_at": None,
                "progress": 1,
                "error_count": 0,
            }
        }
    )

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique batch job identifier",
    )

    job_postings: List[JobPosting] = Field(
        ...,
        description="List of job postings to process",
        min_length=1,
        max_length=50,
    )

    status: BatchStatus = Field(
        default=BatchStatus.PENDING,
        description="Current processing status",
    )

    results: List[SearchResult] = Field(
        default_factory=list,
        description="Completed search results",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When batch was created (UTC)",
    )

    started_at: Optional[datetime] = Field(
        None,
        description="When processing started (UTC)",
    )

    completed_at: Optional[datetime] = Field(
        None,
        description="When processing finished (UTC)",
    )

    progress: int = Field(
        default=0,
        description="Number of job postings processed",
        ge=0,
    )

    error_count: int = Field(
        default=0,
        description="Number of searches that failed",
        ge=0,
    )
