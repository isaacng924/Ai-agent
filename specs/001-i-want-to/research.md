# Research: AI Job Connector Agent

**Feature**: AI Job Connector Agent
**Date**: 2025-10-12
**Phase**: 0 (Research & Technology Selection)

## Research Questions

1. How to set up Amazon Bedrock AgentCore with Gateway primitive?
2. What is the best strategy for HR contact discovery using web search?
3. How to structure prompts for reliable tool invocations and reasoning generation?
4. What error handling patterns work best for agent workflows?
5. How to implement rate limiting and batch processing efficiently?

## 1. Amazon Bedrock AgentCore Setup

### Research Findings

**AgentCore Architecture**:
- AgentCore is a managed service for building and deploying AI agents on AWS
- Supports primitives: Gateway (tool integration), Memory (state persistence), Routing (decision trees)
- Integrates natively with Bedrock models (Claude, Nova, Titan)
- Provides built-in observability via CloudWatch

**Gateway Primitive**:
- Enables agents to call external tools/APIs during reasoning loops
- Tool definition: Function name, description, input schema (JSON Schema), output schema
- Supports synchronous and asynchronous invocations
- Can invoke Lambda functions, API Gateway endpoints, or HTTP APIs

**Setup Steps**:
1. Create agent definition with `agentcore` SDK or CDK
2. Define tool schemas with JSON Schema validation
3. Register tools with Gateway primitive
4. Configure Claude model and system prompts
5. Deploy agent to AgentCore runtime
6. Invoke via `invoke_agent()` API

### Decision: Use AgentCore with Gateway Primitive

**Rationale**:
- Meets hackathon requirement (at least 1 primitive)
- Simplifies tool integration compared to custom orchestration
- Built-in error handling and retry logic
- Native CloudWatch integration for observability
- Production-ready scalability

**Implementation Plan**:
- Use `boto3` client for AgentCore API calls
- Define HR Lookup Tool as Lambda function registered with Gateway
- Use JSON Schema for strict input/output validation
- Configure Claude 3.5 Sonnet as reasoning model
- Optional: Add Memory primitive for contact caching (DynamoDB backend)

### Code Example: Agent Definition

```python
import boto3

agentcore = boto3.client('bedrock-agentcore', region_name='us-west-2')

# Create agent
response = agentcore.create_agent(
    agentName='job-connector-agent',
    foundationModel='anthropic.claude-3-5-sonnet-20250929-v1:0',
    instruction="""You are an AI assistant that helps job seekers find
    HR contacts for job postings. For each job posting, use the hr_lookup
    tool to search for relevant HR contacts. Provide reasoning for why
    each contact is relevant.""",
    actionGroups=[
        {
            'actionGroupName': 'hr-tools',
            'actionGroupExecutor': {
                'lambda': 'arn:aws:lambda:us-west-2:123456789012:function:hr-lookup'
            },
            'apiSchema': {
                's3': {
                    's3BucketName': 'job-connector-schemas',
                    's3ObjectKey': 'hr-lookup-tool.json'
                }
            }
        }
    ]
)
```

## 2. HR Contact Discovery Strategy

### Research Findings

**Web Search APIs**:
- **Tavily API**: AI-optimized search with structured outputs, good LinkedIn coverage
- **Serper API**: Google Search wrapper, reliable but less structured
- **AWS Kendra**: Enterprise search requiring indexed corpus (overkill for this use case)

**Contact Discovery Patterns**:
1. **LinkedIn-First**: Search "Company Name hiring manager Job Title"
2. **Company Website**: Fallback to company careers/about pages
3. **General Web**: News articles, press releases mentioning HR team

**Confidence Scoring**:
- High (0.8-1.0): LinkedIn profile with recent activity, exact title match
- Medium (0.5-0.7): LinkedIn profile, general HR role
- Low (0.3-0.4): Company website mention, inferred from org structure
- Very Low (0.0-0.2): Generic contact form, no specific person found

### Decision: Multi-Stage Search with Tavily

**Rationale**:
- Tavily provides structured JSON output ideal for LLM consumption
- Supports search depth customization (quick vs. comprehensive)
- Better than direct scraping (legal, rate limits, ethical)
- Fallback to Serper if Tavily quota exhausted

**Implementation Plan**:
```python
# Stage 1: LinkedIn search
query = f"{company_name} recruiter {job_title} site:linkedin.com"
results = tavily.search(query, search_depth="advanced", max_results=5)

# Stage 2: Company website (if Stage 1 fails)
if not results:
    query = f"{company_name} careers contact HR"
    results = tavily.search(query, search_depth="basic", max_results=3)

# Stage 3: General web (last resort)
if not results:
    query = f"{company_name} hiring manager {job_title}"
    results = tavily.search(query, search_depth="basic", max_results=3)
```

**Confidence Calculation**:
```python
def calculate_confidence(search_result, job_title):
    confidence = 0.5  # Base confidence

    # Boost for LinkedIn
    if "linkedin.com" in search_result.url:
        confidence += 0.3

    # Boost for title match
    if job_title.lower() in search_result.title.lower():
        confidence += 0.2

    # Boost for recent content
    if "2024" in search_result.date or "2025" in search_result.date:
        confidence += 0.1

    return min(confidence, 1.0)
```

## 3. Prompt Engineering for Reliable Tool Use

### Research Findings

**Claude Tool Use Best Practices**:
- Provide explicit tool descriptions with examples
- Use JSON Schema to enforce output structure
- Include "thinking" step before tool invocation
- Handle tool errors gracefully with retry logic

**Structured Output Techniques**:
- Define Pydantic models for expected outputs
- Use XML tags for structured sections (<reasoning>, <contact>, <confidence>)
- Request JSON with explicit schema in system prompt

### Decision: Structured Prompts with Schema Enforcement

**Contact Discovery Prompt**:
```
You are an expert HR contact researcher. For the given job posting:

1. Analyze the company and job title to determine the most likely HR contact
2. Use the hr_lookup tool to search for contacts
3. Select the most relevant contact based on:
   - Role specificity (engineering recruiter > general HR for tech roles)
   - Recent activity (active on LinkedIn > stale profiles)
   - Department alignment (matches job title domain)

4. Generate reasoning explaining your selection

Output format:
{
  "contact_name": "Full Name",
  "contact_role": "Title at Company",
  "profile_url": "https://linkedin.com/in/...",
  "confidence": 0.85,
  "reasoning": "This person is the Engineering Recruiter at TechCorp,
                actively posting about open tech positions in the last month."
}
```

**Reasoning Generation Prompt**:
```
Given the job posting context and discovered HR contact, explain WHY
this contact is the best match. Consider:

- Role specialization (does their title match the job domain?)
- Recent hiring activity (evidence of active recruitment?)
- Company size (appropriate level of contact for org size?)
- Alternative contacts considered (why was this one chosen?)

Reasoning should be 2-3 sentences, specific and actionable.
```

## 4. Error Handling Patterns

### Research Findings

**Agent Workflow Errors**:
- Tool invocation failures (API rate limits, network errors)
- No contacts found (company too small, no public HR presence)
- Ambiguous company names (multiple entities with same name)
- Malformed input (missing company or job title)

**Error Recovery Strategies**:
- Retry with exponential backoff (3 attempts, 1s → 2s → 4s delays)
- Fallback to alternative tools (Tavily → Serper → mock data)
- Graceful degradation (return "No contact found" with explanation)
- User-actionable error messages (suggest corrections)

### Decision: Multi-Level Error Handling

**Implementation**:
```python
class ContactDiscoveryError(Exception):
    """Base exception for contact discovery failures"""
    pass

class RateLimitError(ContactDiscoveryError):
    """API rate limit exceeded"""
    pass

class NoContactFoundError(ContactDiscoveryError):
    """No HR contact could be identified"""
    pass

def discover_contact_with_retry(job_posting, max_retries=3):
    for attempt in range(max_retries):
        try:
            return tavily_search(job_posting)
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                # Fallback to Serper
                return serper_search(job_posting)
        except NoContactFoundError as e:
            # Don't retry, return structured error
            return {
                "contact_name": None,
                "reasoning": f"No contact found: {str(e)}",
                "suggestions": ["Try company careers page", "LinkedIn direct search"]
            }
```

**User-Facing Error Messages**:
- ✅ Good: "No HR contact found for TechCorp. The company may not have public HR profiles. Try searching their careers page directly."
- ❌ Bad: "API error 429: Rate limit exceeded"

## 5. Rate Limiting and Batch Processing

### Research Findings

**Tavily Rate Limits**:
- Free tier: 1000 searches/month
- Pro tier: 10,000 searches/month
- Rate: ~10 requests/second

**Batch Processing Patterns**:
- Sequential: Simple but slow (5 postings × 60s = 5 min)
- Parallel: Faster but risks rate limits (10 concurrent → 10 API calls/sec)
- Queue-based: Optimal for large batches with rate limit respect

### Decision: Parallel with Rate Limiting

**Implementation**:
```python
import asyncio
from asyncio import Semaphore

async def process_batch_with_limit(job_postings, max_concurrent=3):
    semaphore = Semaphore(max_concurrent)  # Limit to 3 concurrent searches

    async def rate_limited_discovery(posting):
        async with semaphore:
            result = await discover_contact(posting)
            await asyncio.sleep(0.5)  # 500ms delay between requests
            return result

    tasks = [rate_limited_discovery(p) for p in job_postings]
    return await asyncio.gather(*tasks)
```

**Performance Target**:
- 10 job postings with 3 concurrent workers and 500ms delays:
  - Sequential: 10 × 60s = 600s (10 min)
  - Parallel (3 workers): (10 / 3) × 60s = 200s (3.3 min) ✅ Meets < 5 min requirement

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|------------|-----------|
| LLM | Claude 3.5 Sonnet (Bedrock) | Strong reasoning, structured output, hackathon compliant |
| Orchestration | Bedrock AgentCore | Gateway primitive, built-in lifecycle management |
| Web Search | Tavily API (Serper fallback) | AI-optimized, structured JSON, good LinkedIn coverage |
| Backend | Python 3.11 | Ecosystem for AI/ML, Bedrock SDK support, async capabilities |
| Storage | S3 + optional DynamoDB | Inputs/outputs in S3, contact caching in DynamoDB (Memory) |
| Infrastructure | AWS CDK (Python) | Type-safe, composable, easier AgentCore setup than SAM |
| Testing | pytest + moto | Standard Python testing, AWS service mocking |
| Observability | CloudWatch Logs + Metrics | Native AgentCore integration |

## Next Steps (Phase 1)

1. **Data Models**: Define Pydantic schemas for JobPosting, HRContact, SearchResult, BatchJob
2. **Contracts**: Create JSON Schema for AgentCore input/output and Gateway tool
3. **Quickstart**: Write step-by-step local setup and demo walkthrough
4. **Re-run Constitution Check**: Verify Phase 1 design maintains compliance

## References

- [Amazon Bedrock AgentCore Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Claude Tool Use Guide](https://docs.anthropic.com/claude/docs/tool-use)
- [Tavily API Documentation](https://docs.tavily.com/)
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
