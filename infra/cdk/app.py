#!/usr/bin/env python3
"""CDK app entry point for AI Job Connector deployment."""

import os
from aws_cdk import App, Environment
from stacks.ecs_fargate_stack import ECSFargateStack

app = App()

# Get AWS account and region from environment or use defaults
env = Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
)

# Create the ECS Fargate stack
ECSFargateStack(
    app,
    "AIJobConnectorStack",
    env=env,
    description="AI Job Connector - Streamlit Web App on ECS Fargate",
)

app.synth()
