# Data Model: AI Job Connector Agent

**Feature**: AI Job Connector Agent
**Date**: 2025-10-12
**Phase**: 1 (Design & Contracts)

## Overview

This document defines the data entities, schemas, and relationships for the Job Connector Agent. All models use Pydantic for validation and serialization.

## Core Entities

### 1. JobPosting

**Purpose**: Represents a job opportunity the user wants to find HR contacts for.

**Schema**:
```python
from pydantic import BaseModel, Field
from typing import Optional

class JobPosting(BaseModel):
    """A job posting submitted by the user for HR contact discovery."""

    company_name: str = Field(
        ...,
        description="Official company name (e.g., 'Anthropic', 'Amazon Web Services')",
        min_length=1,
        max_length=200
    )

    job_title: str = Field(
        ...,
        description="Job title or role name (e.g., 'Senior Software Engineer')",
        min_length=1,
        max_length=200
    )

    description: Optional[str] = Field(
        None,
        description="Optional job description or requirements for better context",
        max_length=5000
    )

    job_url: Optional[str] = Field(
        None,
        description="Optional URL to the job posting",
        pattern=r"^https?://.*"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "Anthropic",
                "job_title": "AI Safety Researcher",
                "description": "Research alignment and safety for large language models",
                "job_url": "https://anthropic.com/careers/ai-safety-researcher"
            }
        }
```

**Validation Rules**:
- `company_name` and `job_title` are required
- Both must be non-empty strings (1-200 chars)
- `description` is optional but capped at 5000 characters
- `job_url` must be valid HTTP/HTTPS URL if provided

**Relationships**:
- One JobPosting → One or more SearchResult entities
- Part of BatchJob entity (one-to-many)

---

### 2. HRContact

**Purpose**: Represents a discovered HR or recruitment professional at a company.

**Schema**:
```python
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from enum import Enum

class ContactSource(str, Enum):
    """Source of HR contact discovery"""
    LINKEDIN = "linkedin"
    COMPANY_WEBSITE = "company_website"
    WEB_SEARCH = "web_search"
    CACHED = "cached"
    INFERRED = "inferred"

class HRContact(BaseModel):
    """An HR or recruiter contact discovered for a job posting."""

    name: str = Field(
        ...,
        description="Full name of the HR contact",
        min_length=1,
        max_length=200
    )

    role: str = Field(
        ...,
        description="Job title or role at the company (e.g., 'Senior Technical Recruiter')",
        min_length=1,
        max_length=200
    )

    company: str = Field(
        ...,
        description="Company name (should match JobPosting.company_name)",
        min_length=1,
        max_length=200
    )

    profile_url: Optional[HttpUrl] = Field(
        None,
        description="LinkedIn profile or professional network URL"
    )

    source: ContactSource = Field(
        ...,
        description="How this contact was discovered"
    )

    confidence_score: float = Field(
        ...,
        description="Confidence in contact relevance (0.0 - 1.0)",
        ge=0.0,
        le=1.0
    )

    additional_info: Optional[dict] = Field(
        None,
        description="Optional metadata (recent activity, department, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jane Smith",
                "role": "Engineering Recruiter",
                "company": "Anthropic",
                "profile_url": "https://linkedin.com/in/janesmith",
                "source": "linkedin",
                "confidence_score": 0.9,
                "additional_info": {
                    "department": "Engineering",
                    "recent_activity": "Posted about AI hiring 2 weeks ago"
                }
            }
        }
```

**Validation Rules**:
- All core fields (name, role, company) are required
- `profile_url` is optional but must be valid URL if provided
- `confidence_score` must be between 0.0 and 1.0
- `source` must be one of the defined ContactSource enum values

**Confidence Score Interpretation**:
- **0.9-1.0**: High confidence (LinkedIn profile, exact role match, recent activity)
- **0.7-0.8**: Medium-high confidence (LinkedIn profile, general HR role)
- **0.5-0.6**: Medium confidence (Company website mention, inferred role)
- **0.3-0.4**: Low confidence (Generic web search result)
- **0.0-0.2**: Very low confidence (No specific person found, contact form)

**Relationships**:
- Part of SearchResult entity (one-to-one)
- May be cached in Memory primitive (DynamoDB) for reuse

---

### 3. SearchResult

**Purpose**: Represents the complete result of contact discovery for a single job posting.

**Schema**:
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SearchResult(BaseModel):
    """Result of HR contact discovery for a job posting."""

    job_posting: JobPosting = Field(
        ...,
        description="The original job posting that was searched"
    )

    hr_contact: Optional[HRContact] = Field(
        None,
        description="Discovered HR contact (None if not found)"
    )

    reasoning: str = Field(
        ...,
        description="Explanation of why this contact was selected (or why none found)",
        min_length=10,
        max_length=1000
    )

    search_duration_seconds: float = Field(
        ...,
        description="Time taken for contact discovery",
        ge=0.0
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this search was performed (UTC)"
    )

    error_message: Optional[str] = Field(
        None,
        description="Error message if search failed"
    )

    suggestions: Optional[list[str]] = Field(
        None,
        description="Suggestions for user if no contact found"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "job_posting": {
                    "company_name": "Anthropic",
                    "job_title": "AI Safety Researcher"
                },
                "hr_contact": {
                    "name": "Jane Smith",
                    "role": "Engineering Recruiter",
                    "company": "Anthropic",
                    "profile_url": "https://linkedin.com/in/janesmith",
                    "source": "linkedin",
                    "confidence_score": 0.9
                },
                "reasoning": "Jane Smith is Anthropic's Engineering Recruiter with a focus on AI research roles. Her LinkedIn shows recent posts about hiring for the safety team.",
                "search_duration_seconds": 12.5,
                "timestamp": "2025-10-12T14:30:00Z",
                "error_message": None,
                "suggestions": None
            }
        }
```

**Validation Rules**:
- `job_posting` is always required (the input)
- `hr_contact` is optional (None if not found)
- `reasoning` is always required (explains selection OR explains failure)
- `reasoning` must be 10-1000 characters (substantive explanation)
- `search_duration_seconds` must be non-negative

**State Transitions**:
```
START → SEARCHING → [SUCCESS: hr_contact populated] → END
                 → [FAILURE: hr_contact=None, error_message set] → END
```

**Relationships**:
- Contains one JobPosting (composition)
- Contains zero or one HRContact (composition)
- Part of BatchJob results array

---

### 4. BatchJob

**Purpose**: Represents a batch of job postings submitted together for processing.

**Schema**:
```python
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from enum import Enum
import uuid

class BatchStatus(str, Enum):
    """Status of batch job processing"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"

class BatchJob(BaseModel):
    """A batch of job postings for HR contact discovery."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique batch job identifier"
    )

    job_postings: List[JobPosting] = Field(
        ...,
        description="List of job postings to process",
        min_length=1,
        max_length=50
    )

    status: BatchStatus = Field(
        default=BatchStatus.PENDING,
        description="Current processing status"
    )

    results: List[SearchResult] = Field(
        default_factory=list,
        description="Completed search results"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When batch was created (UTC)"
    )

    started_at: Optional[datetime] = Field(
        None,
        description="When processing started (UTC)"
    )

    completed_at: Optional[datetime] = Field(
        None,
        description="When processing finished (UTC)"
    )

    progress: int = Field(
        default=0,
        description="Number of job postings processed",
        ge=0
    )

    error_count: int = Field(
        default=0,
        description="Number of searches that failed",
        ge=0
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "job_postings": [
                    {"company_name": "Anthropic", "job_title": "AI Safety Researcher"},
                    {"company_name": "TechCorp", "job_title": "Senior Engineer"}
                ],
                "status": "in_progress",
                "results": [],
                "created_at": "2025-10-12T14:00:00Z",
                "started_at": "2025-10-12T14:00:05Z",
                "completed_at": None,
                "progress": 1,
                "error_count": 0
            }
        }
```

**Validation Rules**:
- `job_postings` must contain 1-50 entries (hackathon scope)
- `progress` must be ≤ length of `job_postings`
- `results` should contain `progress` number of entries
- `error_count` ≤ `progress`

**State Transitions**:
```
PENDING → IN_PROGRESS → [all successful] → COMPLETED
                      → [some failed] → PARTIALLY_COMPLETED
                      → [all failed] → FAILED
```

**Relationships**:
- Contains many JobPosting entities (composition)
- Contains many SearchResult entities (composition)
- One BatchJob represents one user request

---

### 5. OutreachMessage (Optional - P4)

**Purpose**: Represents a generated personalized outreach message for an HR contact.

**Schema**:
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class MessageTone(str, Enum):
    """Tone style for generated messages"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    ENTHUSIASTIC = "enthusiastic"

class MessageChannel(str, Enum):
    """Delivery channel for the message"""
    LINKEDIN = "linkedin"
    EMAIL = "email"
    GENERIC = "generic"

class OutreachMessage(BaseModel):
    """A personalized outreach message for an HR contact."""

    hr_contact: HRContact = Field(
        ...,
        description="The HR contact this message is for"
    )

    job_posting: JobPosting = Field(
        ...,
        description="The job posting context"
    )

    subject: str = Field(
        ...,
        description="Email subject line or LinkedIn message title",
        min_length=5,
        max_length=200
    )

    body: str = Field(
        ...,
        description="Message content",
        min_length=50,
        max_length=2000
    )

    tone: MessageTone = Field(
        default=MessageTone.PROFESSIONAL,
        description="Message tone style"
    )

    channel: MessageChannel = Field(
        ...,
        description="Intended delivery channel"
    )

    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When message was generated (UTC)"
    )

    personalization_notes: Optional[str] = Field(
        None,
        description="Notes on personalization elements used"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "hr_contact": {
                    "name": "Jane Smith",
                    "role": "Engineering Recruiter",
                    "company": "Anthropic"
                },
                "job_posting": {
                    "company_name": "Anthropic",
                    "job_title": "AI Safety Researcher"
                },
                "subject": "Interested in AI Safety Researcher Role",
                "body": "Hi Jane,\n\nI noticed you're recruiting for the AI Safety Researcher position at Anthropic. I have 5 years of experience in ML safety research...",
                "tone": "professional",
                "channel": "linkedin",
                "generated_at": "2025-10-12T15:00:00Z",
                "personalization_notes": "Referenced recent LinkedIn post about safety team hiring"
            }
        }
```

**Validation Rules**:
- `subject` must be 5-200 characters
- `body` must be 50-2000 characters (concise but substantive)
- All references (hr_contact, job_posting) are required

**Relationships**:
- References one HRContact (foreign key relationship)
- References one JobPosting (foreign key relationship)
- Optional extension of SearchResult

---

## Entity Relationships Diagram

```
┌─────────────┐
│  BatchJob   │
│             │
│ - id        │
│ - status    │
│ - progress  │
└──────┬──────┘
       │ 1
       │ contains
       │ *
┌──────▼─────────┐
│  JobPosting    │
│                │
│ - company_name │
│ - job_title    │
│ - description  │
└──────┬─────────┘
       │ 1
       │ produces
       │ 1
┌──────▼─────────────┐
│  SearchResult      │
│                    │
│ - reasoning        │
│ - search_duration  │
│ - timestamp        │
└──────┬─────────────┘
       │ 1
       │ contains
       │ 0..1
┌──────▼──────────┐       ┌────────────────────┐
│   HRContact     │──────>│ OutreachMessage    │
│                 │ 1   * │ (Optional - P4)    │
│ - name          │       │                    │
│ - role          │       │ - subject          │
│ - profile_url   │       │ - body             │
│ - confidence    │       │ - tone             │
└─────────────────┘       └────────────────────┘
```

## Data Flow

```
User Input (JSON/CSV)
        │
        ▼
┌───────────────┐
│   BatchJob    │ Created with PENDING status
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  JobPosting   │ Validated and parsed
└───────┬───────┘
        │
        ▼
   Agent Runtime
   (AgentCore)
        │
        ▼
┌───────────────┐
│  HR Lookup    │ Gateway tool invoked
│     Tool      │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│   HRContact   │ Discovered (or None if not found)
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ SearchResult  │ Packaged with reasoning
└───────┬───────┘
        │
        ▼
┌───────────────┐
│   BatchJob    │ Status updated to COMPLETED
│  .results[]   │
└───────────────┘
        │
        ▼
Output (JSON/CSV/S3)
```

## Storage Strategy

### S3 Storage (Inputs/Outputs)

**Bucket Structure**:
```
job-connector-inputs/
├── {batch_id}/
│   └── job_postings.json

job-connector-outputs/
├── {batch_id}/
│   ├── results.json
│   ├── results.csv
│   └── summary.txt

job-connector-logs/
├── {batch_id}/
│   └── agent_execution.log
```

### DynamoDB Storage (Optional - Memory Primitive)

**Table**: `job-connector-hr-contacts`

**Schema**:
- **Partition Key**: `company_name` (string)
- **Sort Key**: `role` (string)
- **Attributes**: `name`, `profile_url`, `confidence_score`, `last_updated`, `source`

**Purpose**: Cache discovered HR contacts to speed up repeated searches

**TTL**: 30 days (contacts may change roles)

## Validation Examples

### Valid JobPosting
```json
{
  "company_name": "Anthropic",
  "job_title": "AI Safety Researcher",
  "description": "Research alignment techniques for large language models",
  "job_url": "https://anthropic.com/careers"
}
```

### Valid SearchResult (Success)
```json
{
  "job_posting": {
    "company_name": "Anthropic",
    "job_title": "AI Safety Researcher"
  },
  "hr_contact": {
    "name": "Jane Smith",
    "role": "Engineering Recruiter",
    "company": "Anthropic",
    "profile_url": "https://linkedin.com/in/janesmith",
    "source": "linkedin",
    "confidence_score": 0.9
  },
  "reasoning": "Jane Smith is Anthropic's Engineering Recruiter with a focus on AI research roles. Recent LinkedIn activity shows posts about hiring for the safety team.",
  "search_duration_seconds": 12.5,
  "timestamp": "2025-10-12T14:30:00Z"
}
```

### Valid SearchResult (Failure - No Contact Found)
```json
{
  "job_posting": {
    "company_name": "SmallStartup Inc",
    "job_title": "Engineer"
  },
  "hr_contact": null,
  "reasoning": "No public HR presence found for SmallStartup Inc. The company appears to have fewer than 10 employees based on web search results.",
  "search_duration_seconds": 8.2,
  "timestamp": "2025-10-12T14:35:00Z",
  "error_message": "No HR contact found",
  "suggestions": [
    "Check the company's careers page for a contact form",
    "Try reaching out directly to the founder on LinkedIn"
  ]
}
```

## Next Steps

1. Implement Pydantic models in `src/models/` matching these schemas
2. Create JSON Schema files for AgentCore tool contracts (see `contracts/`)
3. Add validation unit tests in `tests/unit/test_models.py`
4. Document serialization examples in quickstart guide
