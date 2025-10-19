"""Web search tools for HR contact discovery using Tavily and Serper APIs."""

import logging
import requests
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from src.utils.config import get_config

logger = logging.getLogger(__name__)


class SearchTool(ABC):
    """Abstract base class for search tools."""

    @abstractmethod
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Execute a search query.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search result dictionaries
        """
        pass


class TavilySearchTool(SearchTool):
    """
    Web search using Tavily API.

    Tavily is optimized for AI agents and provides clean, structured results.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tavily search tool.

        Args:
            api_key: Tavily API key (uses config if not provided)
        """
        self.config = get_config()
        self.api_key = api_key or self.config.tavily_api_key

        if not self.api_key:
            raise ValueError("Tavily API key is required")

        self.api_url = "https://api.tavily.com/search"
        self.timeout = self.config.search_timeout_seconds

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Execute a Tavily search.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of search results with title, url, content, and score
        """
        try:
            logger.info(f"Executing Tavily search: {query}")

            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "advanced",
                "max_results": min(max_results, self.config.max_search_results),
                "include_domains": [
                    "linkedin.com",
                    "indeed.com",
                    "glassdoor.com",
                ],  # Focus on professional networks
            }

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            logger.info(f"Tavily search returned {len(results)} results")
            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"Tavily search failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Tavily search: {str(e)}")
            raise


class SerperSearchTool(SearchTool):
    """
    Web search using Serper API (fallback option).

    Serper provides Google search results via API.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Serper search tool.

        Args:
            api_key: Serper API key (uses config if not provided)
        """
        self.config = get_config()
        self.api_key = api_key or self.config.serper_api_key

        if not self.api_key:
            raise ValueError("Serper API key is required")

        self.api_url = "https://google.serper.dev/search"
        self.timeout = self.config.search_timeout_seconds

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Execute a Serper search.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of search results with title, url, and snippet
        """
        try:
            logger.info(f"Executing Serper search: {query}")

            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json",
            }

            payload = {
                "q": query,
                "num": min(max_results, self.config.max_search_results),
            }

            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            results = data.get("organic", [])

            # Normalize Serper results to match Tavily format
            normalized_results = [
                {
                    "title": result.get("title"),
                    "url": result.get("link"),
                    "content": result.get("snippet"),
                    "score": 1.0,  # Serper doesn't provide scores
                }
                for result in results
            ]

            logger.info(f"Serper search returned {len(normalized_results)} results")
            return normalized_results

        except requests.exceptions.RequestException as e:
            logger.error(f"Serper search failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Serper search: {str(e)}")
            raise


def search_hr_contacts(
    company_name: str,
    job_title: str,
    max_results: int = 10,
    prefer_tavily: bool = True,
) -> List[Dict[str, Any]]:
    """
    Search for HR contacts at a company (high-level convenience function).

    Args:
        company_name: Name of the company
        job_title: Job title to help target relevant recruiters
        max_results: Maximum number of results
        prefer_tavily: If True, try Tavily first, fallback to Serper

    Returns:
        List of search results

    Raises:
        ValueError: If no API keys are configured
        requests.exceptions.RequestException: If all search attempts fail
    """
    config = get_config()

    # Construct search query
    query = f"{company_name} recruiter {job_title} site:linkedin.com"
    logger.info(f"Searching for HR contacts with query: {query}")

    # Try Tavily first if preferred and available
    if prefer_tavily and config.tavily_api_key:
        try:
            tool = TavilySearchTool()
            return tool.search(query, max_results)
        except Exception as e:
            logger.warning(f"Tavily search failed, trying fallback: {str(e)}")

    # Try Serper as fallback
    if config.serper_api_key:
        try:
            tool = SerperSearchTool()
            return tool.search(query, max_results)
        except Exception as e:
            logger.error(f"Serper search also failed: {str(e)}")
            raise

    # No API keys available
    raise ValueError(
        "No search API keys configured. Set TAVILY_API_KEY or SERPER_API_KEY in environment."
    )
