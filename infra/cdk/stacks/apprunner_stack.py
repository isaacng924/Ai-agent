"""AWS App Runner stack for AI Job Connector Streamlit app."""

from aws_cdk import (
    Stack,
    CfnOutput,
    aws_apprunner as apprunner,
    aws_ecr_assets as ecr_assets,
    aws_iam as iam,
)
from constructs import Construct
import os


class AppRunnerStack(Stack):
    """Stack for deploying Streamlit app to AWS App Runner."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Build and push Docker image to ECR
        docker_image_asset = ecr_assets.DockerImageAsset(
            self,
            "StreamlitAppImage",
            directory=os.path.join(os.path.dirname(__file__), "../../.."),  # Root of project
            platform=ecr_assets.Platform.LINUX_AMD64,
        )

        # Create IAM role for App Runner instance
        instance_role = iam.Role(
            self,
            "AppRunnerInstanceRole",
            assumed_by=iam.ServicePrincipal("tasks.apprunner.amazonaws.com"),
            description="IAM role for App Runner instance to access AWS services",
        )

        # Grant Bedrock access
        instance_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=["*"],
            )
        )

        # Optional: Grant DynamoDB access if caching is enabled
        instance_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                ],
                resources=["arn:aws:dynamodb:*:*:table/job-connector-*"],
            )
        )

        # Create IAM role for App Runner service to access ECR
        access_role = iam.Role(
            self,
            "AppRunnerAccessRole",
            assumed_by=iam.ServicePrincipal("build.apprunner.amazonaws.com"),
            description="IAM role for App Runner to pull images from ECR",
        )

        # Grant ECR access
        docker_image_asset.repository.grant_pull(access_role)

        # Get environment variables from context or use defaults
        tavily_api_key = self.node.try_get_context("tavily_api_key") or os.environ.get("TAVILY_API_KEY", "")
        aws_region = self.region or "us-west-2"
        bedrock_model_id = self.node.try_get_context("bedrock_model_id") or "anthropic.claude-3-5-sonnet-20250929-v1:0"

        # Create App Runner service
        app_runner_service = apprunner.CfnService(
            self,
            "StreamlitAppRunnerService",
            source_configuration=apprunner.CfnService.SourceConfigurationProperty(
                authentication_configuration=apprunner.CfnService.AuthenticationConfigurationProperty(
                    access_role_arn=access_role.role_arn
                ),
                image_repository=apprunner.CfnService.ImageRepositoryProperty(
                    image_identifier=docker_image_asset.image_uri,
                    image_repository_type="ECR",
                    image_configuration=apprunner.CfnService.ImageConfigurationProperty(
                        port="8501",
                        runtime_environment_variables=[
                            apprunner.CfnService.KeyValuePairProperty(
                                name="AWS_REGION",
                                value=aws_region,
                            ),
                            apprunner.CfnService.KeyValuePairProperty(
                                name="TAVILY_API_KEY",
                                value=tavily_api_key,
                            ),
                            apprunner.CfnService.KeyValuePairProperty(
                                name="BEDROCK_MODEL_ID",
                                value=bedrock_model_id,
                            ),
                            apprunner.CfnService.KeyValuePairProperty(
                                name="AGENT_NAME",
                                value="job-connector-agent",
                            ),
                            apprunner.CfnService.KeyValuePairProperty(
                                name="MAX_SEARCH_RESULTS",
                                value="10",
                            ),
                        ],
                    ),
                ),
                auto_deployments_enabled=False,
            ),
            instance_configuration=apprunner.CfnService.InstanceConfigurationProperty(
                cpu="1 vCPU",
                memory="2 GB",
                instance_role_arn=instance_role.role_arn,
            ),
            health_check_configuration=apprunner.CfnService.HealthCheckConfigurationProperty(
                protocol="HTTP",
                path="/_stcore/health",
                interval=10,
                timeout=5,
                healthy_threshold=1,
                unhealthy_threshold=5,
            ),
            service_name="ai-job-connector-web",
        )

        # Output the App Runner service URL
        CfnOutput(
            self,
            "AppRunnerServiceURL",
            value=f"https://{app_runner_service.attr_service_url}",
            description="URL of the deployed Streamlit app",
            export_name="AIJobConnectorURL",
        )

        CfnOutput(
            self,
            "AppRunnerServiceId",
            value=app_runner_service.attr_service_id,
            description="App Runner Service ID",
        )
