"""AgentRuntime for interacting with Amazon Bedrock AgentCore."""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from src.utils.config import get_config
from src.utils.aws_clients import get_bedrock_runtime_client
from src.agent.prompts import SYSTEM_PROMPT, format_contact_discovery_prompt
from src.models.job_posting import JobPosting
from src.models.hr_contact import HRContact
from src.models.search_result import SearchResult
from src.models import ContactSource
from src.tools.hr_lookup import HRLookupTool

logger = logging.getLogger(__name__)


class AgentRuntime:
    """
    Runtime wrapper for Amazon Bedrock AgentCore interactions.

    Handles:
    - Agent invocation with tools
    - Streaming responses
    - Tool result handling
    - Error recovery
    """

    def __init__(self, agent_id: Optional[str] = None, agent_alias_id: Optional[str] = None):
        """
        Initialize AgentRuntime.

        Args:
            agent_id: Bedrock Agent ID (optional, for deployed agents)
            agent_alias_id: Bedrock Agent Alias ID (optional)
        """
        self.config = get_config()
        self.client = get_bedrock_runtime_client()
        self.agent_id = agent_id
        self.agent_alias_id = agent_alias_id or "TSTALIASID"  # Default test alias

        # Initialize HR Lookup tool
        self.hr_lookup_tool = HRLookupTool()

        logger.info(
            f"Initialized AgentRuntime with model: {self.config.bedrock_model_id}"
        )

    def discover_contact(
        self, job_posting: JobPosting, session_id: Optional[str] = None
    ) -> SearchResult:
        """
        Discover HR contact for a job posting using the agent.

        Args:
            job_posting: Job posting to search for
            session_id: Optional session ID for conversation continuity

        Returns:
            SearchResult with discovered contact and reasoning
        """
        start_time = datetime.now(timezone.utc)

        try:
            # Format the discovery prompt
            prompt = format_contact_discovery_prompt(
                company_name=job_posting.company_name,
                job_title=job_posting.job_title,
                description=job_posting.description,
            )

            logger.info(
                f"Discovering contact for {job_posting.company_name} - {job_posting.job_title}"
            )

            # Invoke agent with prompt
            response = self._invoke_agent(prompt, session_id)

            # Parse response to extract contact information
            hr_contact = self._parse_contact_from_response(response, job_posting)

            # Calculate duration
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()

            # Create search result
            result = SearchResult(
                job_posting=job_posting,
                hr_contact=hr_contact,
                reasoning=response.get("reasoning", "Contact discovered via agent search"),
                search_duration_seconds=duration,
                timestamp=datetime.now(timezone.utc),
            )

            logger.info(
                f"Successfully discovered contact for {job_posting.company_name}: "
                f"{hr_contact.name if hr_contact else 'None'}"
            )

            return result

        except Exception as e:
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.error(f"Error discovering contact: {str(e)}", exc_info=True)

            # Return failed search result
            return SearchResult(
                job_posting=job_posting,
                hr_contact=None,
                reasoning="Search failed due to technical error",
                search_duration_seconds=duration,
                timestamp=datetime.now(timezone.utc),
                error_message=str(e),
                suggestions=[
                    "Try visiting the company careers page directly",
                    "Search LinkedIn manually for recruiters at this company",
                    f"Check {job_posting.company_name}'s website for HR contact information",
                ],
            )

    def _invoke_agent(
        self, prompt: str, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke the Bedrock agent with a prompt.

        Args:
            prompt: User prompt for the agent
            session_id: Optional session ID

        Returns:
            Parsed agent response
        """
        if self.agent_id:
            # Use deployed agent
            return self._invoke_deployed_agent(prompt, session_id)
        else:
            # Use direct model invocation (for development/testing)
            return self._invoke_model_directly(prompt)

    def _invoke_deployed_agent(
        self, prompt: str, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke a deployed Bedrock agent.

        Args:
            prompt: User prompt
            session_id: Session ID for continuity

        Returns:
            Agent response
        """
        session_id = session_id or f"session-{datetime.now(timezone.utc).timestamp()}"

        response = self.client.invoke_agent(
            agentId=self.agent_id,
            agentAliasId=self.agent_alias_id,
            sessionId=session_id,
            inputText=prompt,
        )

        # Process streaming response
        completion = ""
        for event in response.get("completion", []):
            if "chunk" in event:
                chunk = event["chunk"]
                if "bytes" in chunk:
                    completion += chunk["bytes"].decode("utf-8")

        return {"completion": completion, "raw_response": response}

    def _invoke_model_directly(self, prompt: str) -> Dict[str, Any]:
        """
        Invoke Bedrock model directly with tool support.

        Used for development and testing before agent deployment.

        Args:
            prompt: User prompt

        Returns:
            Model response with tool results integrated
        """
        bedrock_runtime = get_bedrock_runtime_client()
        model_id = self.config.bedrock_model_id

        # Prepare tool definition
        tools = [
            {
                "name": "hr_lookup",
                "description": "Search for HR contacts and recruiters at a specific company. Returns LinkedIn profiles and professional contact information for recruiters who handle the specified type of role.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "Name of the target company (e.g., 'Anthropic', 'Amazon')"
                        },
                        "job_title": {
                            "type": "string",
                            "description": "Job title to help identify relevant recruiters (e.g., 'Software Engineer', 'Data Scientist')"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of search results to return",
                            "default": 10
                        }
                    },
                    "required": ["company_name", "job_title"]
                }
            }
        ]

        # Start conversation
        messages = [{"role": "user", "content": prompt}]

        # Tool use loop (max 5 iterations to prevent infinite loops)
        max_iterations = 5
        for iteration in range(max_iterations):
            logger.info(f"Tool loop iteration {iteration + 1}/{max_iterations}")

            # Prepare request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "temperature": 0.7,
                "system": SYSTEM_PROMPT,
                "messages": messages,
                "tools": tools,
            }

            # Invoke model
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
            )

            # Parse response
            response_body = json.loads(response["body"].read())

            # Check stop reason
            stop_reason = response_body.get("stop_reason")

            # Add assistant's response to conversation
            assistant_message = {
                "role": "assistant",
                "content": response_body.get("content", [])
            }
            messages.append(assistant_message)

            # If Claude wants to use a tool
            if stop_reason == "tool_use":
                logger.info("Claude requested tool use")

                # Process tool use requests
                tool_results = []
                for content_block in response_body.get("content", []):
                    if content_block.get("type") == "tool_use":
                        tool_name = content_block.get("name")
                        tool_input = content_block.get("input", {})
                        tool_use_id = content_block.get("id")

                        logger.info(f"Executing tool: {tool_name} with input: {tool_input}")

                        # Execute the tool
                        if tool_name == "hr_lookup":
                            tool_result = self.hr_lookup_tool.execute(tool_input)
                        else:
                            tool_result = {"error": f"Unknown tool: {tool_name}"}

                        logger.info(f"Tool result: {len(str(tool_result))} chars")

                        # Add tool result to results
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": json.dumps(tool_result)
                        })

                # Add tool results to conversation
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

                # Continue loop to get Claude's response after using the tool
                continue

            # If we got a final response (not tool use), extract and return it
            elif stop_reason == "end_turn":
                completion = ""
                for content_block in response_body.get("content", []):
                    if content_block.get("type") == "text":
                        completion += content_block.get("text", "")

                logger.info(f"Received final response: {len(completion)} chars")
                return {
                    "completion": completion,
                    "raw_response": response_body,
                    "reasoning": completion  # Use completion as reasoning
                }

        # If we hit max iterations, return what we have
        logger.warning("Hit max tool iterations, returning last response")
        completion = ""
        for content_block in response_body.get("content", []):
            if content_block.get("type") == "text":
                completion += content_block.get("text", "")

        return {
            "completion": completion or "No response generated",
            "raw_response": response_body,
            "reasoning": "Max iterations reached"
        }

    def _parse_contact_from_response(
        self, response: Dict[str, Any], job_posting: JobPosting
    ) -> Optional[HRContact]:
        """
        Parse HR contact information from agent response.

        Args:
            response: Agent response dictionary
            job_posting: Original job posting

        Returns:
            HRContact if found, None otherwise
        """
        completion = response.get("completion", "")

        # Check if response indicates no contact found
        no_contact_indicators = [
            "could not find",
            "unable to locate",
            "no suitable contact",
            "no results",
            "not found",
            "no contact",
        ]
        if any(indicator in completion.lower() for indicator in no_contact_indicators):
            logger.info("Agent indicated no contact found")
            return None

        # Try to parse JSON if present (structured output)
        import re
        json_match = re.search(r'\{[^{}]*"name"[^{}]*\}', completion, re.DOTALL)
        if json_match:
            try:
                contact_data = json.loads(json_match.group())
                return HRContact(
                    name=contact_data.get("name", "Unknown"),
                    role=contact_data.get("role", "Recruiter"),
                    company=job_posting.company_name,
                    profile_url=contact_data.get("profile_url"),
                    source=ContactSource(contact_data.get("source", "web_search")),
                    confidence_score=float(contact_data.get("confidence_score", 0.7)),
                    additional_info=contact_data.get("additional_info", {}),
                )
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse JSON contact: {e}")

        # Fallback: Extract info from text with better pattern matching
        contact_info = {
            "name": "Unknown",
            "role": "Recruiter",
            "confidence": 0.5,
            "profile_url": None,
        }

        # Try to find "Contact name and role: NAME - ROLE" pattern
        name_role_match = re.search(
            r'(?:Contact name and role|contact):\s*([^-\n]+?)\s*-\s*([^\n]+)',
            completion,
            re.IGNORECASE
        )
        if name_role_match:
            contact_info["name"] = name_role_match.group(1).strip()
            contact_info["role"] = name_role_match.group(2).strip()
            logger.info(f"Extracted name/role from pattern: {contact_info['name']} - {contact_info['role']}")

        # Extract LinkedIn URL
        url_match = re.search(r'(?:Profile URL|linkedin\.com):\s*(https://[^\s\n]+)', completion, re.IGNORECASE)
        if url_match:
            contact_info["profile_url"] = url_match.group(1).strip()
        else:
            # Try to find any LinkedIn URL
            url_match = re.search(r'https://(?:www\.)?linkedin\.com/in/[^\s\)]+', completion)
            if url_match:
                contact_info["profile_url"] = url_match.group(0).strip()

        # Extract confidence score
        conf_match = re.search(r'(?:Confidence score|confidence):\s*(\d+\.?\d*)', completion, re.IGNORECASE)
        if conf_match:
            try:
                confidence = float(conf_match.group(1))
                contact_info["confidence"] = confidence if confidence <= 1 else confidence / 100
            except ValueError:
                pass

        # Only return contact if we found a real name
        if contact_info["name"] != "Unknown" and len(contact_info["name"]) > 2:
            logger.info(f"Parsed contact from text: {contact_info['name']}")
            return HRContact(
                name=contact_info["name"],
                role=contact_info["role"],
                company=job_posting.company_name,
                profile_url=contact_info["profile_url"],
                source=ContactSource.WEB_SEARCH,
                confidence_score=contact_info["confidence"],
                additional_info={
                    "raw_response": completion[:300],
                    "parsing_method": "text_extraction"
                },
            )

        # If we couldn't parse anything useful, return None
        logger.warning("Could not parse usable contact information from response")
        return None
