"""Message generation service for personalized outreach."""

import json
import logging
import time
from typing import Optional
from botocore.exceptions import ClientError

from src.models.cv_profile import CVProfile
from src.models.job_posting import JobPosting
from src.models.hr_contact import HRContact
from src.agent.prompts import format_message_generation_prompt
from src.utils.aws_clients import get_bedrock_runtime_client
from src.utils.config import get_config

logger = logging.getLogger(__name__)


class MessageGenerator:
    """Generate personalized outreach messages using AWS Bedrock."""

    def __init__(self):
        """Initialize message generator with AWS Bedrock client."""
        self.bedrock_runtime = get_bedrock_runtime_client()
        self.config = get_config()
        self.model_id = self.config.bedrock_model_id

    def _invoke_with_retry(self, invoke_func, max_retries=5):
        """
        Invoke a Bedrock function with exponential backoff retry logic.

        Args:
            invoke_func: Function to invoke (should return response)
            max_retries: Maximum number of retry attempts

        Returns:
            Response from invoke_func

        Raises:
            Exception: If all retries are exhausted
        """
        for attempt in range(max_retries):
            try:
                return invoke_func()
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')

                # Check if it's a throttling error
                if error_code in ['ThrottlingException', 'TooManyRequestsException', 'ServiceUnavailable']:
                    if attempt < max_retries - 1:
                        # Calculate exponential backoff: 2^attempt * base_delay
                        base_delay = 2
                        delay = (2 ** attempt) * base_delay + (time.time() % 1)  # Add jitter
                        logger.warning(
                            f"Throttling detected (attempt {attempt + 1}/{max_retries}). "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"Max retries ({max_retries}) exhausted due to throttling")
                        raise
                else:
                    # Non-throttling error, raise immediately
                    logger.error(f"Non-throttling error: {error_code}")
                    raise
            except Exception as e:
                # Non-ClientError exceptions, raise immediately
                logger.error(f"Unexpected error: {str(e)}")
                raise

        raise Exception("Failed to invoke after all retries")

    def generate_message(
        self,
        cv_profile: CVProfile,
        job_posting: JobPosting,
        hr_contact: HRContact,
        tone: str = "professional",
        channel: str = "linkedin",
        length: str = "medium",
    ) -> str:
        """
        Generate a personalized outreach message.

        Args:
            cv_profile: Candidate's CV profile
            job_posting: Target job posting
            hr_contact: HR contact to reach out to
            tone: Message tone (professional, friendly, formal, enthusiastic)
            channel: Delivery channel (linkedin, email, generic)
            length: Message length (short, medium, long)

        Returns:
            Generated personalized message

        Raises:
            Exception: If message generation fails
        """
        logger.info(
            f"Generating {tone} {channel} message for "
            f"{job_posting.company_name} - {job_posting.job_title}"
        )

        # Format the prompt
        prompt = format_message_generation_prompt(
            job_seeker_info=cv_profile.to_summary_text(),
            company_name=job_posting.company_name,
            job_title=job_posting.job_title,
            description=job_posting.description or "Not provided",
            contact_name=hr_contact.name,
            contact_role=hr_contact.role,
            profile_url=str(hr_contact.profile_url) if hr_contact.profile_url else "Not available",
            tone=tone,
            channel=channel,
            length=length,
        )

        # Call Bedrock to generate message
        try:
            response_body = self._invoke_bedrock(prompt)
            message = self._extract_message_from_response(response_body)

            logger.info(
                f"Successfully generated message ({len(message)} chars) for "
                f"{hr_contact.name} at {job_posting.company_name}"
            )

            return message

        except Exception as e:
            logger.error(
                f"Failed to generate message for {job_posting.company_name}: {str(e)}"
            )
            raise

    def _invoke_bedrock(self, prompt: str) -> dict:
        """
        Invoke AWS Bedrock with the given prompt.

        Args:
            prompt: User prompt for message generation

        Returns:
            Response body from Bedrock

        Raises:
            Exception: If Bedrock invocation fails
        """
        system_prompt = """You are an expert career advisor and professional communication specialist.
Your role is to generate personalized, authentic, and effective outreach messages for job seekers
contacting HR professionals and recruiters.

Key principles:
1. Be genuine and professional - avoid generic templates
2. Highlight relevant skills/experience that match the role
3. Keep the message concise and respectful of the recipient's time
4. Include a clear call-to-action
5. Adapt tone and format to the specified channel (LinkedIn vs email)
6. Make it personal by referencing specific details about the company/role

Generate messages that feel human-written, not AI-generated."""

        # Prepare request body
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7,  # Slightly higher for more creative messages
        }

        # Invoke Bedrock with retry logic
        response = self._invoke_with_retry(
            lambda: self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
            )
        )

        # Parse response
        response_body = json.loads(response["body"].read())
        return response_body

    def _extract_message_from_response(self, response_body: dict) -> str:
        """
        Extract the generated message from Bedrock response.

        Args:
            response_body: Response body from Bedrock

        Returns:
            Extracted message text

        Raises:
            ValueError: If message cannot be extracted
        """
        try:
            # Extract content from Claude response
            content_blocks = response_body.get("content", [])

            if not content_blocks:
                raise ValueError("No content in Bedrock response")

            # Get text from first content block
            message = content_blocks[0].get("text", "").strip()

            if not message:
                raise ValueError("Empty message in Bedrock response")

            return message

        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract message from response: {str(e)}")
            logger.debug(f"Response body: {response_body}")
            raise ValueError(f"Invalid response format: {str(e)}")

    def generate_batch_messages(
        self,
        cv_profile: CVProfile,
        job_postings: list[JobPosting],
        hr_contacts: list[HRContact],
        tone: str = "professional",
        channel: str = "linkedin",
        length: str = "medium",
    ) -> list[str]:
        """
        Generate messages for multiple job postings.

        Args:
            cv_profile: Candidate's CV profile
            job_postings: List of target job postings
            hr_contacts: List of HR contacts (must match job_postings length)
            tone: Message tone
            channel: Delivery channel
            length: Message length

        Returns:
            List of generated messages

        Raises:
            ValueError: If job_postings and hr_contacts lengths don't match
        """
        if len(job_postings) != len(hr_contacts):
            raise ValueError(
                f"Mismatch: {len(job_postings)} job postings but {len(hr_contacts)} contacts"
            )

        messages = []

        for job_posting, hr_contact in zip(job_postings, hr_contacts):
            try:
                if hr_contact:  # Only generate if contact was found
                    message = self.generate_message(
                        cv_profile=cv_profile,
                        job_posting=job_posting,
                        hr_contact=hr_contact,
                        tone=tone,
                        channel=channel,
                        length=length,
                    )
                    messages.append(message)
                else:
                    messages.append("")  # No contact found

            except Exception as e:
                logger.error(
                    f"Failed to generate message for {job_posting.company_name}: {str(e)}"
                )
                messages.append("")  # Failed to generate

        return messages
