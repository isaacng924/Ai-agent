"""CVProfile data model for parsed resume/CV data."""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CVProfile(BaseModel):
    """Parsed CV/resume data for message personalization."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-234-567-8900",
                "summary": "Experienced software engineer with 5 years in full-stack development",
                "skills": ["Python", "AWS", "React", "Machine Learning"],
                "experience": [
                    "Senior Software Engineer at TechCorp (2020-2025)",
                    "Software Engineer at StartupXYZ (2018-2020)"
                ],
                "education": [
                    "B.S. Computer Science - MIT (2018)"
                ],
                "raw_text": "Full CV text content..."
            }
        }
    )

    full_name: Optional[str] = Field(
        None,
        description="Candidate's full name",
        max_length=200,
    )

    email: Optional[str] = Field(
        None,
        description="Contact email",
        max_length=200,
    )

    phone: Optional[str] = Field(
        None,
        description="Contact phone number",
        max_length=50,
    )

    summary: Optional[str] = Field(
        None,
        description="Professional summary or objective",
        max_length=1000,
    )

    skills: List[str] = Field(
        default_factory=list,
        description="List of skills and technologies",
    )

    experience: List[str] = Field(
        default_factory=list,
        description="Work experience entries",
    )

    education: List[str] = Field(
        default_factory=list,
        description="Education background",
    )

    raw_text: str = Field(
        ...,
        description="Full raw text extracted from CV",
        min_length=1,
    )

    def to_summary_text(self) -> str:
        """
        Generate a concise summary for message generation prompts.

        Returns:
            Formatted summary text suitable for Claude prompts
        """
        parts = []

        if self.full_name:
            parts.append(f"Name: {self.full_name}")

        if self.summary:
            parts.append(f"Summary: {self.summary}")

        if self.skills:
            skills_str = ", ".join(self.skills[:10])  # Limit to top 10
            parts.append(f"Key Skills: {skills_str}")

        if self.experience:
            exp_str = " | ".join(self.experience[:3])  # Limit to top 3
            parts.append(f"Experience: {exp_str}")

        if self.education:
            edu_str = " | ".join(self.education[:2])  # Limit to top 2
            parts.append(f"Education: {edu_str}")

        return "\n".join(parts)
