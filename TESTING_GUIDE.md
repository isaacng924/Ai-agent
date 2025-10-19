# Testing Guide - AI Job Connector Agent

This guide shows you how to manually test the MVP without any real API keys!

## Quick Start (No APIs Required) 🚀

### 1. Setup (First Time Only)

```bash
# Navigate to project
cd /Users/isaac/Documents/aws_hackathon/ai-agent

# Activate virtual environment (already created)
source .venv/bin/activate

# Verify installation
job-connector-mock --help
```

### 2. Run the Comprehensive Mock Test Suite

```bash
python test_mock.py
```

**What you'll see:**
- ✅ Test 1: Single job search
- ✅ Test 2: Batch processing (5 jobs)
- ✅ Test 3: JSON export
- Beautiful formatted output with tables
- Realistic mock data for Anthropic, OpenAI, Google, etc.

**Expected output:**
```
✅ All Mock Tests Passed!

What this demonstrates:
  • Single job search functionality
  • Batch processing of multiple jobs
  • JSON export capabilities
  • Realistic contact discovery
  • Reasoning generation
```

### 3. Test the Mock CLI

#### Demo Mode (Easiest)

```bash
job-connector-mock demo
```

This runs with 3 sample job postings and shows:
- Progress indicators
- Formatted results table
- Detailed reasoning for each contact
- All without any API keys!

#### Single Search

```bash
job-connector-mock search \
  --company "Anthropic" \
  --title "AI Safety Researcher" \
  --output result.json
```

#### Batch Processing

Create a test file:

```bash
cat > my_jobs.json << 'EOF'
[
  {
    "company_name": "Anthropic",
    "job_title": "AI Safety Researcher"
  },
  {
    "company_name": "OpenAI",
    "job_title": "Software Engineer"
  },
  {
    "company_name": "Tesla",
    "job_title": "Autopilot Engineer"
  }
]
EOF
```

Process it:

```bash
job-connector-mock batch \
  --file my_jobs.json \
  --output results.json
```

Check the output:

```bash
cat results.json | jq '.'
```

## What the Mock Version Does

### Realistic Mock Data

The mock version returns realistic fake data for:

- **Anthropic**: Sarah Chen (Senior Technical Recruiter, AI Research)
- **OpenAI**: Rachel Goldberg (Talent Partner)
- **Google DeepMind**: Emily Watson (Research Recruiter)
- **Amazon/AWS**: James Rodriguez (Technical Recruiting Manager)
- **Microsoft**: Michael Kim (Senior Recruiter, AI & Cloud)
- **Meta**: Amanda Torres (Engineering Recruiter, AI Infrastructure)
- **Tesla**: Lisa Zhang (Recruiting Lead, Autopilot)
- **Nvidia**: David Lee (Technical Recruiter, GPU & AI Hardware)
- **Hugging Face**: Thomas Müller (Head of Talent)
- **And more...**

### Features Demonstrated

✅ **All core functionality works:**
- Job posting validation
- Contact discovery
- Reasoning generation
- Confidence scoring
- Batch processing
- Progress tracking
- JSON export
- Error handling
- Rich CLI output

✅ **No external dependencies:**
- No AWS credentials needed
- No Tavily API key needed
- No internet connection needed
- Pure Python with realistic mock data

## Unit Tests

Run the pytest suite:

```bash
pytest tests/ -v
```

**Expected output:**
```
tests/test_config.py::TestConfig::test_config_validation_valid_model_id PASSED
tests/test_config.py::TestConfig::test_config_validation_invalid_model_id PASSED
tests/test_config.py::TestConfig::test_config_validation_log_level PASSED
tests/test_config.py::TestGetConfig::test_get_config_from_env PASSED
tests/test_config.py::TestGetConfig::test_get_config_missing_required_vars PASSED
tests/test_config.py::TestGetConfig::test_get_config_optional_vars PASSED
tests/test_models.py::TestJobPosting::test_create_valid_job_posting PASSED
tests/test_models.py::TestJobPosting::test_job_posting_minimal PASSED
tests/test_models.py::TestJobPosting::test_job_posting_validation_errors PASSED
tests/test_models.py::TestHRContact::test_create_valid_hr_contact PASSED
tests/test_models.py::TestHRContact::test_hr_contact_confidence_validation PASSED
tests/test_models.py::TestSearchResult::test_create_search_result_with_contact PASSED
tests/test_models.py::TestSearchResult::test_create_search_result_without_contact PASSED
tests/test_models.py::TestBatchJob::test_create_batch_job PASSED
tests/test_models.py::TestBatchJob::test_batch_job_validation PASSED

========================= 15 passed =========================
```

## Component Tests

### Test Individual Models

```bash
python << 'EOF'
from src.models.job_posting import JobPosting
from src.models.hr_contact import HRContact
from src.models import ContactSource

# Create job posting
job = JobPosting(
    company_name="Anthropic",
    job_title="AI Researcher"
)
print(f"✓ Job: {job.company_name} - {job.job_title}")

# Create HR contact
contact = HRContact(
    name="Sarah Chen",
    role="Technical Recruiter",
    company="Anthropic",
    source=ContactSource.LINKEDIN,
    confidence_score=0.95
)
print(f"✓ Contact: {contact.name} ({contact.confidence_score})")
print("✅ Models work correctly!")
EOF
```

### Test Mock Search

```bash
python << 'EOF'
from src.tools.mock_search import mock_search_hr_contacts

results = mock_search_hr_contacts("Anthropic", "AI Researcher", max_results=3)
print(f"✓ Found {len(results)} mock results")
for r in results:
    print(f"  - {r['title']}")
print("✅ Mock search works!")
EOF
```

### Test Mock Runtime

```bash
python << 'EOF'
from src.models.job_posting import JobPosting
from src.agent.mock_runtime import MockAgentRuntime

job = JobPosting(company_name="OpenAI", job_title="Software Engineer")
runtime = MockAgentRuntime()
result = runtime.discover_contact(job)

print(f"✓ Job: {result.job_posting.company_name}")
print(f"✓ Contact: {result.hr_contact.name}")
print(f"✓ Reasoning: {result.reasoning[:80]}...")
print("✅ Mock runtime works!")
EOF
```

## Validation Checklist

Run through this checklist to validate everything works:

- [ ] **Unit tests pass**: `pytest tests/ -v` (15/15 passed)
- [ ] **Mock test suite passes**: `python test_mock.py` (All 3 tests pass)
- [ ] **Mock CLI help works**: `job-connector-mock --help`
- [ ] **Mock demo works**: `job-connector-mock demo`
- [ ] **Single search works**: `job-connector-mock search -c "Anthropic" -t "AI Researcher"`
- [ ] **Batch processing works**: `job-connector-mock batch -f my_jobs.json -o results.json`
- [ ] **JSON output is valid**: `cat results.json | jq '.'`
- [ ] **Models validate correctly**: Run component tests above
- [ ] **Mock search returns data**: Run mock search test above
- [ ] **Mock runtime works**: Run mock runtime test above

## Output Examples

### Single Search Result

```json
{
  "job_posting": {
    "company_name": "Anthropic",
    "job_title": "AI Safety Researcher"
  },
  "hr_contact": {
    "name": "Sarah Chen",
    "role": "Senior Technical Recruiter, AI Research",
    "company": "Anthropic",
    "profile_url": "https://linkedin.com/in/sarahchen-anthropic",
    "source": "linkedin",
    "confidence_score": 0.95
  },
  "reasoning": "Sarah Chen is the Senior Technical Recruiter...",
  "search_duration_seconds": 1.66
}
```

### Batch Results Summary

```json
{
  "batch_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "total_jobs": 5,
  "successful": 5,
  "failed": 0,
  "results": [...]
}
```

## Next Steps: Testing with Real APIs

Once you have API keys configured, you can test with the real CLI:

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env and add:
# - AWS_REGION=us-west-2
# - BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20250929-v1:0
# - TAVILY_API_KEY=tvly-your-key
```

### 2. Verify AWS Access

```bash
aws sts get-caller-identity
aws bedrock list-foundation-models --region us-west-2 | grep claude
```

### 3. Test Real CLI

```bash
# Real demo (requires APIs)
job-connector demo

# Real search (requires APIs)
job-connector search -c "Anthropic" -t "AI Researcher"

# Real batch (requires APIs)
job-connector batch -f my_jobs.json -o results.json
```

## Troubleshooting

### Mock CLI not found

```bash
# Reinstall package
pip install -e .

# Verify installation
pip show ai-job-connector
job-connector-mock --help
```

### Import errors

```bash
# Check you're in virtual environment
which python  # Should show .venv path

# Reinstall dependencies
pip install -e ".[dev]"
```

### Tests fail

```bash
# Clean reinstall
pip uninstall ai-job-connector -y
pip install -e ".[dev]"
pytest tests/ -v
```

## Performance Expectations

**Mock Mode:**
- Single search: ~1-2 seconds (simulated delay)
- Batch of 5 jobs: ~5-10 seconds
- Batch of 10 jobs: ~10-20 seconds

**Real Mode (with APIs):**
- Single search: ~5-15 seconds (real API calls)
- Batch of 5 jobs: ~30-60 seconds
- Batch of 10 jobs: ~60-120 seconds

## What to Expect

### Mock Mode ✅
- Instant setup (no configuration needed)
- Realistic fake data
- Demonstrates all functionality
- Perfect for development and demos
- Shows correct data models and flow

### Real Mode (Future) 🔜
- Requires AWS Bedrock access
- Requires Tavily or Serper API key
- Returns actual HR contacts from LinkedIn
- Real AI reasoning from Claude
- Production-ready results

## Summary

The mock version lets you:
1. ✅ Test all functionality immediately
2. ✅ Verify the system works end-to-end
3. ✅ See realistic output and formatting
4. ✅ Validate data models and contracts
5. ✅ Demo the agent without API keys
6. ✅ Develop new features safely

**You can fully test the MVP right now without any API keys!**

Run `python test_mock.py` to see the full system in action! 🚀
