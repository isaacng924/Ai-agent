"""HRContact data model."""

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from src.models import ContactSource


class HRContact(BaseModel):
    """An HR or recruiter contact discovered for a job posting."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jane Smith",
                "role": "Engineering Recruiter",
                "company": "Anthropic",
                "profile_url": "https://linkedin.com/in/janesmith",
                "source": "linkedin",
                "confidence_score": 0.9,
                "additional_info": {
                    "department": "Engineering",
                    "recent_activity": "Posted about AI hiring 2 weeks ago",
                },
            }
        }
    )

    name: str = Field(
        ...,
        description="Full name of the HR contact",
        min_length=1,
        max_length=200,
    )

    role: str = Field(
        ...,
        description="Job title or role at the company (e.g., 'Senior Technical Recruiter')",
        min_length=1,
        max_length=200,
    )

    company: str = Field(
        ...,
        description="Company name (should match JobPosting.company_name)",
        min_length=1,
        max_length=200,
    )

    profile_url: Optional[HttpUrl] = Field(
        None,
        description="LinkedIn profile or professional network URL",
    )

    source: ContactSource = Field(
        ...,
        description="How this contact was discovered",
    )

    confidence_score: float = Field(
        ...,
        description="Confidence in contact relevance (0.0 - 1.0)",
        ge=0.0,
        le=1.0,
    )

    additional_info: Optional[dict] = Field(
        None,
        description="Optional metadata (recent activity, department, etc.)",
    )
