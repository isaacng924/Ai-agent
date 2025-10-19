# AI Job Connector Agent - Quickstart Guide

Get started with the AI Job Connector Agent in under 10 minutes.

## Prerequisites

- Python 3.11 or higher
- AWS Account with Bedrock access
- AWS CLI configured with credentials
- (Optional) Tavily API key for web search

## Installation

### 1. Clone and Set Up Virtual Environment

```bash
cd ai-agent
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install the package and its dependencies
pip install -e .

# For development (includes testing tools)
pip install -e ".[dev]"
```

### 3. Configure Environment Variables

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Edit `.env` and set your configuration:

```bash
# Required
AWS_REGION=us-west-2
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20250929-v1:0

# Optional but recommended for better results
TAVILY_API_KEY=tvly-your-key-here  # Get from https://tavily.com

# Optional
AWS_PROFILE=default  # If using named profiles
SERPER_API_KEY=your-serper-key  # Fallback search provider
```

### 4. Verify AWS Bedrock Access

Ensure your AWS credentials have access to Amazon Bedrock:

```bash
aws bedrock list-foundation-models --region us-west-2
```

You should see Claude models in the output.

## Quick Start Usage

### Run the Demo

Test the agent with sample job postings:

```bash
job-connector demo
```

This will:
- Load 3 sample job postings from test fixtures
- Process each one to discover HR contacts
- Display results in a formatted table

### Search for a Single Contact

Find an HR contact for a specific job:

```bash
job-connector search \
  --company "Anthropic" \
  --title "AI Safety Researcher" \
  --description "Work on AI alignment and safety research"
```

Example with output file:

```bash
job-connector search \
  -c "Amazon Web Services" \
  -t "Senior Software Engineer - ML" \
  -o results.json
```

### Process Multiple Jobs (Batch Mode)

Create a JSON file with your job postings:

```json
[
  {
    "company_name": "Anthropic",
    "job_title": "AI Researcher"
  },
  {
    "company_name": "OpenAI",
    "job_title": "Software Engineer",
    "description": "Build scalable ML infrastructure"
  }
]
```

Process the batch:

```bash
job-connector batch -f jobs.json -o results.json
```

## Output Format

### Single Search Result

```json
{
  "job_posting": {
    "company_name": "Anthropic",
    "job_title": "AI Safety Researcher"
  },
  "hr_contact": {
    "name": "Sarah Chen",
    "role": "Senior Technical Recruiter - AI Research",
    "company": "Anthropic",
    "profile_url": "https://linkedin.com/in/sarahchen",
    "source": "linkedin",
    "confidence_score": 0.95
  },
  "reasoning": "Sarah Chen is Anthropic's primary recruiter for AI research roles...",
  "search_duration_seconds": 8.2,
  "timestamp": "2025-10-17T10:30:00Z"
}
```

### Batch Results

```json
{
  "batch_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "total_jobs": 10,
  "successful": 9,
  "failed": 1,
  "results": [...]
}
```

## Development and Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_models.py -v
```

### Code Quality

```bash
# Type checking
mypy src/

# Linting
ruff check .
```

## Next Steps

### For Development

1. **Add AWS CDK Infrastructure**: Deploy the agent to AWS with proper AgentCore integration
2. **Implement Memory Primitive**: Cache discovered contacts in DynamoDB
3. **Add Message Generation**: Implement User Story 4 for personalized outreach messages
4. **Set Up CI/CD**: Add GitHub Actions for testing and deployment

### For Production Use

1. **Get API Keys**:
   - Tavily API (recommended): https://tavily.com
   - Serper API (fallback): https://serper.dev

2. **Configure AWS**:
   - Set up Bedrock model access in your region
   - Create IAM role with Bedrock permissions
   - Configure VPC and security groups if deploying to Lambda

3. **Deploy**:
   ```bash
   make deploy  # Deploys CDK stack (when implemented)
   ```

## Troubleshooting

### "Configuration error: AWS_REGION environment variable is required"

Make sure you've created a `.env` file and set AWS_REGION:

```bash
cp .env.example .env
# Edit .env and set AWS_REGION=us-west-2
```

### "No search API keys configured"

The agent needs either Tavily or Serper API key for web search:

1. Get a Tavily API key from https://tavily.com (recommended)
2. Add it to your `.env` file:
   ```
   TAVILY_API_KEY=tvly-your-key-here
   ```

### Tests failing with Pydantic warnings

The warnings about deprecated Pydantic V1 style are non-critical. To fix:

- Update validators in `src/utils/config.py` to use `@field_validator`
- Update `Config` classes to use `ConfigDict`

### AWS Bedrock access denied

Ensure your AWS credentials have the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude*"
    }
  ]
}
```

## CLI Reference

### Global Options

- `--verbose` / `-v`: Enable verbose logging

### Commands

#### `search`

Search for HR contacts for a single job posting.

**Options:**
- `--company` / `-c`: Company name (required)
- `--title` / `-t`: Job title (required)
- `--description` / `-d`: Job description (optional)
- `--url` / `-u`: Job posting URL (optional)
- `--output` / `-o`: Output file path (optional)

#### `batch`

Process multiple job postings from a JSON file.

**Options:**
- `--file` / `-f`: Input JSON file (required)
- `--output` / `-o`: Output file path (optional)

#### `demo`

Run a demo with sample job postings from test fixtures.

## Support

For issues or questions:
- Check the [README.md](README.md) for detailed documentation
- Review the [AWS Bedrock AgentCore documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- Open an issue on the project repository
