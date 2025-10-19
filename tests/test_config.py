"""Test configuration management."""

import pytest
import os
from unittest.mock import patch

from src.utils.config import Config, get_config


class TestConfig:
    """Test Config model and validation."""

    def test_config_validation_valid_model_id(self):
        """Test that valid Bedrock model IDs are accepted."""
        valid_ids = [
            "anthropic.claude-3-5-sonnet-20250929-v1:0",
            "anthropic.claude-v2",
            "amazon.titan-text-express-v1",
            "ai21.j2-ultra-v1",
        ]

        for model_id in valid_ids:
            config = Config(
                aws_region="us-west-2",
                bedrock_model_id=model_id,
            )
            assert config.bedrock_model_id == model_id

    def test_config_validation_invalid_model_id(self):
        """Test that invalid Bedrock model IDs are rejected."""
        with pytest.raises(ValueError, match="Invalid Bedrock model ID"):
            Config(
                aws_region="us-west-2",
                bedrock_model_id="invalid-model-id",
            )

    def test_config_validation_log_level(self):
        """Test log level validation."""
        # Valid log levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            config = Config(
                aws_region="us-west-2",
                bedrock_model_id="anthropic.claude-v2",
                log_level=level,
            )
            assert config.log_level == level

        # Case insensitive
        config = Config(
            aws_region="us-west-2",
            bedrock_model_id="anthropic.claude-v2",
            log_level="info",
        )
        assert config.log_level == "INFO"

        # Invalid log level
        with pytest.raises(ValueError, match="Invalid log level"):
            Config(
                aws_region="us-west-2",
                bedrock_model_id="anthropic.claude-v2",
                log_level="INVALID",
            )


class TestGetConfig:
    """Test get_config function."""

    @patch.dict(
        os.environ,
        {
            "AWS_REGION": "us-east-1",
            "BEDROCK_MODEL_ID": "anthropic.claude-v2",
            "TAVILY_API_KEY": "test-key",
        },
    )
    def test_get_config_from_env(self):
        """Test loading config from environment variables."""
        config = get_config(force_reload=True)

        assert config.aws_region == "us-east-1"
        assert config.bedrock_model_id == "anthropic.claude-v2"
        assert config.tavily_api_key == "test-key"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_config_missing_required_vars(self):
        """Test that missing required variables raise errors."""
        with pytest.raises(ValueError, match="AWS_REGION"):
            get_config(force_reload=True)

    @patch.dict(
        os.environ,
        {
            "AWS_REGION": "us-west-2",
            "BEDROCK_MODEL_ID": "anthropic.claude-v2",
            "MAX_SEARCH_RESULTS": "25",
        },
    )
    def test_get_config_optional_vars(self):
        """Test that optional variables are handled correctly."""
        config = get_config(force_reload=True)

        assert config.max_search_results == 25
        assert config.tavily_api_key is None
        assert config.serper_api_key is None
