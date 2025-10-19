# AWS Deployment Guide - AI Job Connector

This guide walks you through deploying the AI Job Connector Streamlit web app to AWS App Runner using AWS CDK.

## Prerequisites

Before deploying, ensure you have:

- [x] **AWS Account** with appropriate permissions
- [x] **AWS CLI** installed and configured (`aws configure`)
- [x] **Docker** installed and running
- [x] **Python 3.11+** installed
- [x] **Node.js** (for AWS CDK CLI)
- [x] **Tavily API Key** (for web search)

### Install AWS CDK CLI

```bash
npm install -g aws-cdk
```

Verify installation:
```bash
cdk --version
```

## Step 1: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and fill in your credentials:
```bash
# Required
TAVILY_API_KEY=tvly-your-actual-api-key-here
AWS_REGION=us-west-2

# Optional (defaults are usually fine)
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20250929-v1:0
```

**Important:** Never commit `.env` to git!

## Step 2: Verify AWS Credentials

Ensure your AWS CLI is configured:

```bash
aws sts get-caller-identity
```

You should see your AWS account details. If not, run:
```bash
aws configure
```

## Step 3: Bootstrap CDK (First Time Only)

If this is your first time using CDK in your AWS account/region:

```bash
make bootstrap-cdk
```

Or manually:
```bash
cd infra/cdk
cdk bootstrap
cd ../..
```

This creates the necessary AWS resources for CDK to deploy your app.

## Step 4: Test Docker Build Locally (Optional but Recommended)

Before deploying, test the Docker image locally:

```bash
# Build the image
make docker-build

# Run it locally (visits http://localhost:8501)
make docker-run
```

**Note:** The container automatically mounts your AWS credentials from `~/.aws/` directory.

### Alternative: Pass AWS Credentials as Environment Variables

If you prefer not to mount credentials, you can pass them as environment variables:

```bash
docker run -p 8501:8501 \
  --env-file .env \
  -e AWS_ACCESS_KEY_ID=your-access-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret-key \
  -e AWS_SESSION_TOKEN=your-session-token \
  ai-job-connector:latest
```

Press `Ctrl+C` to stop the container.

## Step 5: Deploy to AWS App Runner

### Option A: Quick Deploy (Recommended)

```bash
make deploy-full
```

This will:
1. Install CDK dependencies
2. Build the Docker image
3. Push to Amazon ECR
4. Deploy to App Runner
5. Display your app URL

### Option B: Manual Step-by-Step Deploy

```bash
# 1. Install CDK dependencies
make install-cdk

# 2. Synthesize CloudFormation template (optional, for review)
make synth

# 3. Deploy
make deploy
```

## Step 6: Get Your App URL

After deployment completes (5-10 minutes), get your app URL:

```bash
make get-url
```

Or check the deployment status:
```bash
make status
```

You'll get a URL like: `https://abc123xyz.us-west-2.awsapprunner.com`

## Step 7: Access Your App

Open the URL in your browser and start using the AI Job Connector!

## Updating Your Deployment

When you make code changes, redeploy with:

```bash
make deploy
```

CDK will detect changes and update only what's necessary.

## Troubleshooting

### Issue: "ProfileNotFound" or AWS credentials error when testing locally

**Error:**
```
botocore.exceptions.ProfileNotFound: The config profile (default) could not be found
```

**Solution:** This happens when Docker can't access your AWS credentials.

**Option 1 - Use mounted credentials (recommended):**
```bash
# The updated Makefile now automatically mounts ~/.aws
make docker-run
```

**Option 2 - Pass credentials as environment variables:**
```bash
# Export your AWS credentials first
export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)

# Then run with environment variables
docker run -p 8501:8501 \
  --env-file .env \
  -e AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY \
  -e AWS_REGION=us-west-2 \
  ai-job-connector:latest
```

**Option 3 - Skip local testing and deploy directly:**
```bash
# AWS App Runner will use IAM roles, so credentials aren't an issue
make deploy-full
```

### Issue: "No space left on device" during Docker build

**Solution:** Clean up Docker:
```bash
docker system prune -a
```

### Issue: "User is not authorized to perform: bedrock:InvokeModel"

**Solution:** Ensure your AWS account has access to Amazon Bedrock and the Claude model:
1. Go to AWS Console → Bedrock → Model access
2. Request access to Claude 3.5 Sonnet
3. Wait for approval (usually instant)

### Issue: CDK deploy fails with "Tavily API key not set"

**Solution:** Check your `.env` file and ensure `TAVILY_API_KEY` is set correctly.

You can also pass it via CDK context:
```bash
cd infra/cdk
cdk deploy --context tavily_api_key=tvly-your-key-here
```

### Issue: App Runner service unhealthy

**Solution:** Check CloudWatch logs:
```bash
# Get service ARN
aws apprunner list-services --query 'ServiceSummaryList[?ServiceName==`ai-job-connector-web`].ServiceArn' --output text

# View logs (replace SERVICE_ARN)
aws logs tail /aws/apprunner/ai-job-connector-web/SERVICE_ID/application --follow
```

### Issue: "Cannot connect to Docker daemon"

**Solution:** Start Docker Desktop or Docker service:
```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker
```

## Viewing Logs

To view real-time logs from your deployed app:

```bash
# Get your service ID
SERVICE_ID=$(aws apprunner list-services --query 'ServiceSummaryList[?ServiceName==`ai-job-connector-web`].ServiceId' --output text)

# Tail logs
aws logs tail /aws/apprunner/ai-job-connector-web/$SERVICE_ID/application --follow
```

## Monitoring and Costs

### Cost Estimates

AWS App Runner pricing (as of 2024):
- **Provisioned instances:** ~$0.007/hr per GB RAM (~$5/month for 2GB)
- **Active compute:** $0.064/vCPU-hour + $0.007/GB-hour
- **Requests:** $0.0002 per request

**Estimated monthly cost:** $5-20 for low to moderate traffic

### Monitoring

View metrics in AWS Console:
1. Go to **AWS App Runner** → Services → `ai-job-connector-web`
2. Click **Metrics** tab
3. Monitor:
   - Active instances
   - Requests per second
   - Response time
   - CPU/Memory utilization

## Scaling

App Runner auto-scales based on traffic:

- **Min instances:** 1 (default)
- **Max instances:** 25 (default)
- **Scaling:** Automatic based on CPU and request load

To customize, edit `infra/cdk/stacks/apprunner_stack.py`:

```python
auto_scaling_configuration_arn="arn:aws:apprunner:region:account:autoscalingconfiguration/..."
```

## Clean Up / Destroy

To delete all AWS resources and stop incurring charges:

```bash
make destroy
```

**Warning:** This will permanently delete your deployment!

## Security Best Practices

1. **Never commit `.env` to git** - Contains sensitive API keys
2. **Use IAM roles** - CDK creates minimal-privilege roles automatically
3. **Enable AWS CloudTrail** - For audit logging
4. **Rotate API keys regularly** - Update `.env` and redeploy
5. **Use AWS Secrets Manager** (optional) - For production deployments

## Advanced: CI/CD Pipeline

To set up automated deployments from GitHub:

1. Create GitHub Actions workflow (`.github/workflows/deploy.yml`)
2. Add AWS credentials as GitHub Secrets
3. Trigger deployment on push to `main` branch

Example workflow coming soon!

## Support

For issues or questions:
- Check [AWS App Runner documentation](https://docs.aws.amazon.com/apprunner/)
- Review [CDK documentation](https://docs.aws.amazon.com/cdk/)
- File an issue in the project repository

## Architecture Diagram

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────────┐
│  AWS App Runner     │
│  (Streamlit App)    │
│  - Auto-scaling     │
│  - Load balancing   │
└──────┬──────────────┘
       │
       ├─► AWS Bedrock (Claude 3.5 Sonnet)
       │   - HR contact discovery
       │   - Message generation
       │
       ├─► Tavily API (Web Search)
       │   - Company info lookup
       │   - LinkedIn profile search
       │
       └─► Amazon ECR
           - Docker image storage
```

## Next Steps

After successful deployment:

1. Test the app with your CV and job listings
2. Share the URL with users
3. Monitor usage and costs
4. Set up custom domain (optional)
5. Configure alerts for errors/downtime

Happy job hunting! 🚀
