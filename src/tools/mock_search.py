"""Mock search tool for testing without real APIs."""

import logging
import random
import time
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class MockSearchTool:
    """
    Mock search tool that returns realistic fake data.

    Use this for testing without Tavily/Serper API keys.
    """

    def __init__(self):
        """Initialize mock search tool."""
        self.call_count = 0
        logger.info("Initialized MockSearchTool (no real API calls)")

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Mock search that returns realistic fake results.

        Args:
            query: Search query (analyzed to generate relevant mocks)
            max_results: Maximum results to return

        Returns:
            List of mock search results
        """
        self.call_count += 1

        # Simulate API delay
        time.sleep(0.5)

        # Extract company name from query
        company = self._extract_company_from_query(query)

        logger.info(f"Mock search for: {query} (company: {company})")

        # Generate mock results based on company
        results = self._generate_mock_results(company, max_results)

        logger.info(f"Mock search returned {len(results)} results")
        return results

    def _extract_company_from_query(self, query: str) -> str:
        """Extract company name from search query."""
        # Common company names to detect
        companies = [
            "Anthropic", "OpenAI", "Google", "Amazon", "Microsoft",
            "Meta", "Apple", "Tesla", "Nvidia", "Hugging Face",
            "DeepMind", "AWS", "Salesforce", "IBM", "Oracle"
        ]

        for company in companies:
            if company.lower() in query.lower():
                return company

        # Default if not found
        return "Tech Company"

    def _generate_mock_results(self, company: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate realistic mock search results."""

        # Mock recruiter data based on company
        mock_recruiters = {
            "Anthropic": [
                {
                    "title": "Sarah Chen - Senior Technical Recruiter, AI Research @ Anthropic",
                    "url": "https://linkedin.com/in/sarahchen-anthropic",
                    "content": "Senior Technical Recruiter specializing in AI Safety and Research roles at Anthropic. 5+ years experience hiring PhD-level researchers. Based in San Francisco.",
                    "score": 0.95
                },
                {
                    "title": "Michael Zhang - Talent Acquisition Lead @ Anthropic",
                    "url": "https://linkedin.com/in/michaelzhang-ai",
                    "content": "Leading talent acquisition for Anthropic's research and engineering teams. Focus on AI alignment, interpretability, and safety roles.",
                    "score": 0.88
                }
            ],
            "OpenAI": [
                {
                    "title": "Rachel Goldberg - Talent Partner, Research & Engineering @ OpenAI",
                    "url": "https://linkedin.com/in/rachelgoldberg-openai",
                    "content": "Talent Partner at OpenAI focusing on Research Scientists and ML Engineers. Passionate about building diverse AI teams.",
                    "score": 0.92
                },
                {
                    "title": "David Kumar - Senior Recruiter @ OpenAI",
                    "url": "https://linkedin.com/in/davidkumar-openai",
                    "content": "Recruiting top AI talent for OpenAI. Specializing in research and applied engineering roles.",
                    "score": 0.85
                }
            ],
            "Google": [
                {
                    "title": "Emily Watson - Research Recruiter @ Google DeepMind",
                    "url": "https://linkedin.com/in/emilywatson-deepmind",
                    "content": "Recruiting world-class AI researchers for Google DeepMind. Based in London, focusing on reinforcement learning and robotics.",
                    "score": 0.90
                }
            ],
            "Amazon": [
                {
                    "title": "James Rodriguez - Technical Recruiting Manager, AWS AI/ML @ Amazon",
                    "url": "https://linkedin.com/in/jamesrodriguez-aws",
                    "content": "Leading technical recruiting for AWS Machine Learning services. Hiring ML engineers, scientists, and research scientists.",
                    "score": 0.87
                }
            ],
            "Microsoft": [
                {
                    "title": "Michael Kim - Senior Recruiter, AI & Cloud @ Microsoft",
                    "url": "https://linkedin.com/in/michaelkim-msft",
                    "content": "Recruiting for Microsoft AI and Azure teams. Focus on AI researchers, ML engineers, and product managers.",
                    "score": 0.86
                }
            ],
            "Meta": [
                {
                    "title": "Amanda Torres - Engineering Recruiter, AI Infrastructure @ Meta",
                    "url": "https://linkedin.com/in/amandatorres-meta",
                    "content": "Recruiting engineers for Meta's AI infrastructure and PyTorch teams. Looking for distributed systems and ML platform experts.",
                    "score": 0.84
                }
            ],
            "Apple": [
                {
                    "title": "John Park - ML/AI Recruiter, Siri & Speech @ Apple",
                    "url": "https://linkedin.com/in/johnpark-apple",
                    "content": "Recruiting machine learning engineers for Siri and speech technologies. Focus on NLP and voice AI.",
                    "score": 0.83
                }
            ],
            "Tesla": [
                {
                    "title": "Lisa Zhang - Recruiting Lead, Autopilot Team @ Tesla",
                    "url": "https://linkedin.com/in/lisazhang-tesla",
                    "content": "Leading recruitment for Tesla Autopilot. Hiring computer vision engineers and ML researchers.",
                    "score": 0.88
                }
            ],
            "Nvidia": [
                {
                    "title": "David Lee - Technical Recruiter, GPU & AI Hardware @ Nvidia",
                    "url": "https://linkedin.com/in/davidlee-nvidia",
                    "content": "Recruiting hardware engineers for Nvidia's AI chip design teams. Looking for VLSI and computer architecture experts.",
                    "score": 0.85
                }
            ],
            "Hugging Face": [
                {
                    "title": "Thomas Müller - Head of Talent, Engineering @ Hugging Face",
                    "url": "https://linkedin.com/in/thomasmuller-hf",
                    "content": "Building the engineering team at Hugging Face. Open source AI tools and ML infrastructure focus.",
                    "score": 0.91
                }
            ]
        }

        # Get mock data for this company, or generate generic ones
        if company in mock_recruiters:
            results = mock_recruiters[company][:max_results]
        else:
            # Generate generic mock results
            results = [
                {
                    "title": f"HR Manager @ {company} - Talent Acquisition",
                    "url": f"https://linkedin.com/in/recruiter-{company.lower().replace(' ', '')}",
                    "content": f"Recruiting manager at {company}. Focus on technical roles and engineering talent.",
                    "score": 0.75
                }
            ]

        # Add some variety with additional results
        if len(results) < max_results:
            results.append({
                "title": f"{company} Careers Page",
                "url": f"https://{company.lower().replace(' ', '')}.com/careers",
                "content": f"Official careers page for {company}. Apply directly or contact recruiting team.",
                "score": 0.60
            })

        return results[:max_results]


def mock_search_hr_contacts(
    company_name: str,
    job_title: str,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Mock version of search_hr_contacts for testing.

    Args:
        company_name: Name of the company
        job_title: Job title to help target relevant recruiters
        max_results: Maximum number of results

    Returns:
        List of mock search results
    """
    query = f"{company_name} recruiter {job_title} site:linkedin.com"
    tool = MockSearchTool()
    return tool.search(query, max_results)
