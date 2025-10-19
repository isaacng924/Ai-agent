"""Mock agent runtime for testing without AWS Bedrock."""

import logging
import random
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from src.models.job_posting import JobPosting
from src.models.hr_contact import HRContact
from src.models.search_result import SearchResult
from src.models import ContactSource
from src.tools.mock_search import mock_search_hr_contacts

logger = logging.getLogger(__name__)


class MockAgentRuntime:
    """
    Mock agent runtime that simulates Bedrock responses.

    Use this for testing without AWS credentials or API keys.
    """

    def __init__(self):
        """Initialize mock agent runtime."""
        self.invocation_count = 0
        logger.info("Initialized MockAgentRuntime (no real API calls)")

    def discover_contact(
        self, job_posting: JobPosting, session_id: Optional[str] = None
    ) -> SearchResult:
        """
        Mock contact discovery that returns realistic fake data.

        Args:
            job_posting: Job posting to search for
            session_id: Optional session ID

        Returns:
            SearchResult with mock contact and reasoning
        """
        self.invocation_count += 1
        start_time = datetime.now(timezone.utc)

        logger.info(
            f"Mock discovering contact for {job_posting.company_name} - {job_posting.job_title}"
        )

        # Simulate processing time
        time.sleep(random.uniform(0.5, 1.5))

        try:
            # Use mock search to get "results"
            search_results = mock_search_hr_contacts(
                company_name=job_posting.company_name,
                job_title=job_posting.job_title,
                max_results=3
            )

            # Pick the best result (highest score)
            if search_results:
                best_result = max(search_results, key=lambda x: x.get("score", 0))
                hr_contact = self._parse_contact_from_mock_result(
                    best_result, job_posting
                )
                reasoning = self._generate_mock_reasoning(
                    job_posting, hr_contact, best_result
                )
            else:
                hr_contact = None
                reasoning = f"Could not find suitable HR contact for {job_posting.job_title} at {job_posting.company_name}."

            # Calculate duration
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()

            # Create search result
            result = SearchResult(
                job_posting=job_posting,
                hr_contact=hr_contact,
                reasoning=reasoning,
                search_duration_seconds=duration,
                timestamp=datetime.now(timezone.utc),
                suggestions=[
                    f"Visit {job_posting.company_name}'s careers page directly",
                    f"Search LinkedIn for '{job_posting.company_name} recruiter'",
                    f"Try reaching out via {job_posting.company_name}'s general recruiting email"
                ] if not hr_contact else None
            )

            logger.info(
                f"Mock discovered: {hr_contact.name if hr_contact else 'None'}"
            )

            return result

        except Exception as e:
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.error(f"Mock discovery error: {str(e)}", exc_info=True)

            return SearchResult(
                job_posting=job_posting,
                hr_contact=None,
                reasoning="Mock search encountered an error",
                search_duration_seconds=duration,
                timestamp=datetime.now(timezone.utc),
                error_message=str(e),
                suggestions=[
                    "Try the search again",
                    f"Visit {job_posting.company_name} careers page",
                ]
            )

    def _parse_contact_from_mock_result(
        self, result: Dict[str, Any], job_posting: JobPosting
    ) -> Optional[HRContact]:
        """
        Parse HR contact from mock search result.

        Args:
            result: Mock search result dictionary
            job_posting: Original job posting

        Returns:
            HRContact extracted from mock result
        """
        title = result.get("title", "")
        url = result.get("url")
        content = result.get("content", "")
        score = result.get("score", 0.5)

        # Extract name from title (format: "Name - Role @ Company")
        name = "Unknown"
        role = "Recruiter"

        if " - " in title:
            parts = title.split(" - ", 1)
            name = parts[0].strip()
            if " @ " in parts[1]:
                role = parts[1].split(" @ ")[0].strip()
            else:
                role = parts[1].strip()
        elif " @ " in title:
            parts = title.split(" @ ")
            if len(parts[0].split()) <= 3:  # Likely a name
                name = parts[0].strip()
                role = "Recruiter"

        # Determine source
        if "linkedin.com" in url:
            source = ContactSource.LINKEDIN
        elif "careers" in url.lower():
            source = ContactSource.COMPANY_WEBSITE
        else:
            source = ContactSource.WEB_SEARCH

        # Create contact
        contact = HRContact(
            name=name,
            role=role,
            company=job_posting.company_name,
            profile_url=url,
            source=source,
            confidence_score=score,
            additional_info={
                "search_snippet": content[:200],
                "found_via": "mock_search",
                "note": "This is mock data for testing"
            }
        )

        return contact

    def _generate_mock_reasoning(
        self,
        job_posting: JobPosting,
        hr_contact: HRContact,
        search_result: Dict[str, Any]
    ) -> str:
        """
        Generate realistic reasoning for mock contact selection.

        Args:
            job_posting: The job posting
            hr_contact: The selected contact
            search_result: The search result data

        Returns:
            Reasoning string
        """
        # Base reasoning templates
        templates = [
            f"{hr_contact.name} is the {hr_contact.role} at {job_posting.company_name}, specifically focused on roles like {job_posting.job_title}. Their profile shows active recruitment for this department with high relevance to your search.",

            f"Based on LinkedIn data, {hr_contact.name} ({hr_contact.role}) is the primary recruiter for {job_posting.job_title} positions at {job_posting.company_name}. They have demonstrated expertise in this hiring area.",

            f"{hr_contact.name} specializes in recruiting for {job_posting.job_title} roles at {job_posting.company_name}. Their {hr_contact.role} position and recent activity indicate they are the right contact for this opportunity.",

            f"Identified {hr_contact.name} as {hr_contact.role} at {job_posting.company_name} with direct responsibility for {job_posting.job_title} hiring. Their profile shows strong alignment with this role's requirements.",
        ]

        # Pick a random template
        reasoning = random.choice(templates)

        # Add confidence context
        if hr_contact.confidence_score >= 0.9:
            reasoning += " High confidence match based on exact title and department alignment."
        elif hr_contact.confidence_score >= 0.75:
            reasoning += " Strong match with verified profile information."
        else:
            reasoning += " Reasonable match based on available information, though verification recommended."

        return reasoning
