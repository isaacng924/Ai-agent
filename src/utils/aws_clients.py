"""AWS client factory functions for boto3."""

import boto3
from typing import Optional
from functools import lru_cache
from src.utils.config import get_config


@lru_cache(maxsize=1)
def get_bedrock_client():
    """
    Get Amazon Bedrock client (cached).

    Returns:
        boto3 Bedrock client for agent management
    """
    config = get_config()

    session_kwargs = {"region_name": config.aws_region}
    if config.aws_profile:
        session_kwargs["profile_name"] = config.aws_profile

    session = boto3.Session(**session_kwargs)
    return session.client("bedrock-agent")


@lru_cache(maxsize=1)
def get_bedrock_runtime_client():
    """
    Get Amazon Bedrock Runtime client (cached).

    Returns:
        boto3 Bedrock Runtime client for model invocation
    """
    config = get_config()

    session_kwargs = {"region_name": config.aws_region}
    if config.aws_profile:
        session_kwargs["profile_name"] = config.aws_profile

    session = boto3.Session(**session_kwargs)
    return session.client("bedrock-runtime")


@lru_cache(maxsize=1)
def get_s3_client():
    """
    Get Amazon S3 client (cached).

    Returns:
        boto3 S3 client for object storage
    """
    config = get_config()

    session_kwargs = {"region_name": config.aws_region}
    if config.aws_profile:
        session_kwargs["profile_name"] = config.aws_profile

    session = boto3.Session(**session_kwargs)
    return session.client("s3")


@lru_cache(maxsize=1)
def get_secrets_manager_client():
    """
    Get AWS Secrets Manager client (cached).

    Returns:
        boto3 Secrets Manager client for credential retrieval
    """
    config = get_config()

    session_kwargs = {"region_name": config.aws_region}
    if config.aws_profile:
        session_kwargs["profile_name"] = config.aws_profile

    session = boto3.Session(**session_kwargs)
    return session.client("secretsmanager")


def clear_client_cache():
    """Clear all cached boto3 clients (useful for testing)."""
    get_bedrock_client.cache_clear()
    get_bedrock_runtime_client.cache_clear()
    get_s3_client.cache_clear()
    get_secrets_manager_client.cache_clear()
