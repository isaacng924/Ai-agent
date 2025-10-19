"""JobPosting data model."""

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class JobPosting(BaseModel):
    """A job posting submitted by the user for HR contact discovery."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_name": "Anthropic",
                "job_title": "AI Safety Researcher",
                "description": "Research alignment and safety for large language models",
                "job_url": "https://anthropic.com/careers/ai-safety-researcher",
            }
        }
    )

    company_name: str = Field(
        ...,
        description="Official company name (e.g., 'Anthropic', 'Amazon Web Services')",
        min_length=1,
        max_length=200,
    )

    job_title: str = Field(
        ...,
        description="Job title or role name (e.g., 'Senior Software Engineer')",
        min_length=1,
        max_length=200,
    )

    description: Optional[str] = Field(
        None,
        description="Optional job description or requirements for better context",
        max_length=5000,
    )

    job_url: Optional[HttpUrl] = Field(
        None,
        description="Optional URL to the job posting",
    )
