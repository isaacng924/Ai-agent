#!/bin/bash
# Quick deployment script for AI Job Connector

set -e  # Exit on error

echo "========================================="
echo "AI Job Connector - AWS Deployment"
echo "========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found!"
    echo ""
    echo "Please create .env file:"
    echo "  1. cp .env.example .env"
    echo "  2. Edit .env and add your TAVILY_API_KEY"
    echo ""
    exit 1
fi

# Check if TAVILY_API_KEY is set
if ! grep -q "TAVILY_API_KEY=tvly-" .env 2>/dev/null; then
    echo "⚠️  WARNING: TAVILY_API_KEY might not be set correctly in .env"
    echo "   Make sure it starts with 'tvly-'"
    echo ""
fi

# Check AWS credentials
echo "🔍 Checking AWS credentials..."
if ! aws sts get-caller-identity &>/dev/null; then
    echo "❌ ERROR: AWS credentials not configured!"
    echo ""
    echo "Please run: aws configure"
    echo ""
    exit 1
fi

AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region || echo "us-west-2")
echo "✓ AWS Account: $AWS_ACCOUNT"
echo "✓ AWS Region: $AWS_REGION"
echo ""

# Check if CDK is bootstrapped
echo "🔍 Checking CDK bootstrap status..."
if ! aws cloudformation describe-stacks --stack-name CDKToolkit &>/dev/null; then
    echo "⚠️  CDK not bootstrapped in this region."
    echo ""
    read -p "Bootstrap CDK now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 Bootstrapping CDK..."
        make bootstrap-cdk
        echo "✓ CDK bootstrapped"
        echo ""
    else
        echo "❌ Cannot deploy without CDK bootstrap. Exiting."
        exit 1
    fi
else
    echo "✓ CDK already bootstrapped"
    echo ""
fi

# Check if Docker is running
echo "🔍 Checking Docker..."
if ! docker info &>/dev/null; then
    echo "❌ ERROR: Docker is not running!"
    echo ""
    echo "Please start Docker Desktop and try again."
    echo ""
    exit 1
fi
echo "✓ Docker is running"
echo ""

# Ask for confirmation
echo "========================================="
echo "Ready to deploy!"
echo "========================================="
echo ""
echo "This will:"
echo "  1. Install CDK dependencies"
echo "  2. Build Docker image"
echo "  3. Push to Amazon ECR"
echo "  4. Deploy to AWS App Runner"
echo ""
echo "Estimated time: 5-10 minutes"
echo "Estimated cost: ~\$5-20/month"
echo ""
read -p "Continue with deployment? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "🚀 Starting deployment..."
echo ""

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Deploy
make deploy-full

echo ""
echo "========================================="
echo "✓ Deployment complete!"
echo "========================================="
echo ""

# Get the URL
echo "🌐 Getting your app URL..."
URL=$(aws cloudformation describe-stacks --stack-name AIJobConnectorStack \
    --query 'Stacks[0].Outputs[?ExportName==`AIJobConnectorURL`].OutputValue' \
    --output text 2>/dev/null || echo "")

if [ -n "$URL" ]; then
    echo ""
    echo "✓ Your app is available at:"
    echo ""
    echo "  $URL"
    echo ""
    echo "🎉 Happy job hunting!"
else
    echo ""
    echo "⚠️  Could not retrieve URL automatically."
    echo "   Run: make get-url"
    echo ""
fi

echo ""
echo "========================================="
echo "Next steps:"
echo "  - Open the URL in your browser"
echo "  - Upload your CV"
echo "  - Add job listings"
echo "  - Generate HR contacts & messages"
echo ""
echo "Commands:"
echo "  make status   - Check deployment status"
echo "  make get-url  - Get app URL"
echo "  make destroy  - Delete all resources"
echo "========================================="
