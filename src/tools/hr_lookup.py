"""HR Lookup Gateway Tool for Amazon Bedrock AgentCore."""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from src.tools.web_search import search_hr_contacts
from src.models import ContactSource

logger = logging.getLogger(__name__)


class SearchRequest(BaseModel):
    """Request schema for HR contact search."""

    company_name: str = Field(
        ...,
        description="Name of the target company",
        min_length=1,
        max_length=200,
    )

    job_title: str = Field(
        ...,
        description="Job title to help identify relevant recruiters",
        min_length=1,
        max_length=200,
    )

    max_results: int = Field(
        default=10,
        description="Maximum number of search results to return",
        ge=1,
        le=50,
    )


class SearchResponse(BaseModel):
    """Response schema for HR contact search."""

    results: List[Dict[str, Any]] = Field(
        ...,
        description="List of search results with title, url, content, and score",
    )

    query: str = Field(
        ...,
        description="The search query that was executed",
    )

    result_count: int = Field(
        ...,
        description="Number of results returned",
    )

    source: str = Field(
        ...,
        description="Search source (tavily or serper)",
    )


class HRLookupTool:
    """
    Gateway tool for HR contact lookup.

    This tool integrates with Amazon Bedrock AgentCore as a Gateway primitive,
    allowing the agent to perform web searches for HR contacts.
    """

    def __init__(self):
        """Initialize HR Lookup Tool."""
        logger.info("Initialized HRLookupTool")

    def search(self, request: SearchRequest) -> SearchResponse:
        """
        Search for HR contacts at a company.

        Args:
            request: SearchRequest with company_name and job_title

        Returns:
            SearchResponse with search results
        """
        logger.info(
            f"HR Lookup search: {request.company_name} - {request.job_title}"
        )

        try:
            # Execute web search
            results = search_hr_contacts(
                company_name=request.company_name,
                job_title=request.job_title,
                max_results=request.max_results,
            )

            # Construct query string for response
            query = f"{request.company_name} recruiter {request.job_title} site:linkedin.com"

            # Determine which source was used
            from src.utils.config import get_config

            config = get_config()
            source = "tavily" if config.tavily_api_key else "serper"

            response = SearchResponse(
                results=results,
                query=query,
                result_count=len(results),
                source=source,
            )

            logger.info(f"HR Lookup returned {len(results)} results from {source}")
            return response

        except Exception as e:
            logger.error(f"HR Lookup search failed: {str(e)}", exc_info=True)

            # Return empty results on failure
            return SearchResponse(
                results=[],
                query=f"{request.company_name} {request.job_title}",
                result_count=0,
                source="error",
            )

    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Get the tool definition for Bedrock AgentCore Gateway integration.

        Returns:
            Tool definition dictionary matching OpenAPI 3.1.0 schema
        """
        return {
            "toolSpec": {
                "name": "hr_lookup",
                "description": "Search for HR contacts and recruiters at a specific company. Returns LinkedIn profiles and professional contact information.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "company_name": {
                                "type": "string",
                                "description": "Name of the target company (e.g., 'Anthropic', 'Amazon')",
                            },
                            "job_title": {
                                "type": "string",
                                "description": "Job title to help identify relevant recruiters (e.g., 'Software Engineer', 'Data Scientist')",
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of search results to return",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50,
                            },
                        },
                        "required": ["company_name", "job_title"],
                    }
                },
            }
        }

    def execute(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with raw input (for AgentCore integration).

        Args:
            tool_input: Raw tool input dictionary

        Returns:
            Tool result dictionary
        """
        try:
            # Parse input into request model
            request = SearchRequest(**tool_input)

            # Execute search
            response = self.search(request)

            # Return as dictionary
            return response.model_dump()

        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}", exc_info=True)
            return {
                "results": [],
                "query": str(tool_input),
                "result_count": 0,
                "source": "error",
                "error": str(e),
            }
