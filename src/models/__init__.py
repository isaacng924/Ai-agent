"""Data models for AI Job Connector Agent."""

from enum import Enum


class ContactSource(str, Enum):
    """Source of HR contact discovery."""
    LINKEDIN = "linkedin"
    COMPANY_WEBSITE = "company_website"
    WEB_SEARCH = "web_search"
    CACHED = "cached"
    INFERRED = "inferred"


class BatchStatus(str, Enum):
    """Status of batch job processing."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"


class MessageTone(str, Enum):
    """Tone style for generated messages."""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    ENTHUSIASTIC = "enthusiastic"


class MessageChannel(str, Enum):
    """Delivery channel for the message."""
    LINKEDIN = "linkedin"
    EMAIL = "email"
    GENERIC = "generic"


__all__ = [
    "ContactSource",
    "BatchStatus",
    "MessageTone",
    "MessageChannel",
]
