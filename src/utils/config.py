"""Configuration management for the Job Connector Agent."""

import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from dotenv import load_dotenv


class Config(BaseModel):
    """Application configuration loaded from environment variables."""

    model_config = ConfigDict(env_prefix="")

    aws_region: str = Field(
        ...,
        description="AWS region for Bedrock and other services",
    )

    aws_profile: Optional[str] = Field(
        None,
        description="AWS profile to use (optional)",
    )

    bedrock_model_id: str = Field(
        ...,
        description="Bedrock model ID for Claude",
    )

    agent_name: str = Field(
        default="job-connector-agent",
        description="Name of the agent",
    )

    tavily_api_key: Optional[str] = Field(
        None,
        description="Tavily API key for web search",
    )

    serper_api_key: Optional[str] = Field(
        None,
        description="Serper API key for web search (fallback)",
    )

    max_search_results: int = Field(
        default=10,
        description="Maximum number of search results to retrieve",
        ge=1,
        le=50,
    )

    search_timeout_seconds: int = Field(
        default=30,
        description="Timeout for web search requests",
        ge=5,
        le=120,
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    @field_validator("bedrock_model_id")
    @classmethod
    def validate_bedrock_model(cls, v: str) -> str:
        """Ensure Bedrock model ID is valid."""
        # Valid direct model ID prefixes
        valid_prefixes = ["anthropic.claude", "amazon.titan", "ai21."]
        # Valid inference profile prefixes (for cross-region inference)
        valid_inference_prefixes = ["us.", "eu.", "ap."]

        # Check if it's a valid model ID or inference profile
        is_direct_model = any(v.startswith(prefix) for prefix in valid_prefixes)
        is_inference_profile = any(v.startswith(prefix) for prefix in valid_inference_prefixes)

        if not (is_direct_model or is_inference_profile):
            raise ValueError(
                f"Invalid Bedrock model ID: {v}. Must start with one of {valid_prefixes} "
                f"or be an inference profile starting with {valid_inference_prefixes}"
            )
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v_upper


# Global config instance
_config: Optional[Config] = None


def get_config(force_reload: bool = False) -> Config:
    """
    Get application configuration (singleton pattern).

    Args:
        force_reload: If True, reload configuration from environment

    Returns:
        Config instance with validated settings
    """
    global _config

    if _config is None or force_reload:
        # Load .env file if it exists
        load_dotenv()

        # Required environment variables
        aws_region = os.getenv("AWS_REGION")
        if not aws_region:
            raise ValueError("AWS_REGION environment variable is required")

        bedrock_model_id = os.getenv("BEDROCK_MODEL_ID")
        if not bedrock_model_id:
            raise ValueError("BEDROCK_MODEL_ID environment variable is required")

        # Create config with environment variables
        _config = Config(
            aws_region=aws_region,
            aws_profile=os.getenv("AWS_PROFILE"),
            bedrock_model_id=bedrock_model_id,
            agent_name=os.getenv("AGENT_NAME", "job-connector-agent"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            serper_api_key=os.getenv("SERPER_API_KEY"),
            max_search_results=int(os.getenv("MAX_SEARCH_RESULTS", "10")),
            search_timeout_seconds=int(os.getenv("SEARCH_TIMEOUT_SECONDS", "30")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    return _config
