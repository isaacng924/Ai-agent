"""AWS ECS Fargate stack for AI Job Connector Streamlit app."""

from aws_cdk import (
    Stack,
    CfnOutput,
    Duration,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr_assets as ecr_assets,
    aws_iam as iam,
    aws_logs as logs,
)
from constructs import Construct
import os


class ECSFargateStack(Stack):
    """Stack for deploying Streamlit app to ECS Fargate with Application Load Balancer."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Build and push Docker image to ECR
        docker_image_asset = ecr_assets.DockerImageAsset(
            self,
            "StreamlitAppImage",
            directory=os.path.join(os.path.dirname(__file__), "../../.."),  # Root of project
            platform=ecr_assets.Platform.LINUX_AMD64,
        )

        # Use default VPC (or create new one if needed)
        vpc = ec2.Vpc.from_lookup(self, "VPC", is_default=True)

        # Create ECS Cluster
        cluster = ecs.Cluster(
            self,
            "StreamlitCluster",
            vpc=vpc,
            cluster_name="ai-job-connector-cluster",
        )

        # Create Task Role (for container to access AWS services)
        task_role = iam.Role(
            self,
            "ECSTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="IAM role for ECS task to access AWS services",
        )

        # Grant Bedrock access
        task_role.add_to_policy(
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
        task_role.add_to_policy(
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

        # Get environment variables from context or use defaults
        tavily_api_key = self.node.try_get_context("tavily_api_key") or os.environ.get("TAVILY_API_KEY", "")
        aws_region = self.region or "eu-west-1"
        # Use cross-region inference profile for eu-west-1 (required for on-demand throughput)
        bedrock_model_id = self.node.try_get_context("bedrock_model_id") or os.environ.get(
            "BEDROCK_MODEL_ID", "eu.anthropic.claude-3-5-sonnet-20240620-v1:0"
        )

        # Create Fargate Service with Application Load Balancer
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "StreamlitFargateService",
            cluster=cluster,
            cpu=1024,  # 1 vCPU
            memory_limit_mib=2048,  # 2 GB
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_docker_image_asset(docker_image_asset),
                container_port=8501,
                task_role=task_role,
                environment={
                    "AWS_REGION": aws_region,
                    "TAVILY_API_KEY": tavily_api_key,
                    "BEDROCK_MODEL_ID": bedrock_model_id,
                    "AGENT_NAME": "job-connector-agent",
                    "MAX_SEARCH_RESULTS": "10",
                },
                log_driver=ecs.LogDrivers.aws_logs(
                    stream_prefix="streamlit-app",
                    log_retention=logs.RetentionDays.ONE_WEEK,
                ),
            ),
            public_load_balancer=True,
            assign_public_ip=True,  # Enable public IP for ECR access
            service_name="ai-job-connector-web",
        )

        # Configure health check
        fargate_service.target_group.configure_health_check(
            path="/_stcore/health",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(10),
            healthy_threshold_count=2,
            unhealthy_threshold_count=5,
        )

        # Allow inbound traffic on port 8501
        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(8501),
            description="Allow inbound HTTP traffic on Streamlit port",
        )

        # Output the Load Balancer URL
        CfnOutput(
            self,
            "LoadBalancerURL",
            value=f"http://{fargate_service.load_balancer.load_balancer_dns_name}",
            description="URL of the deployed Streamlit app on ECS Fargate",
            export_name="AIJobConnectorURL",
        )

        CfnOutput(
            self,
            "ClusterName",
            value=cluster.cluster_name,
            description="ECS Cluster Name",
        )

        CfnOutput(
            self,
            "ServiceName",
            value=fargate_service.service.service_name,
            description="ECS Service Name",
        )
