# Implementation Plan: AI Job Connector Agent

**Branch**: `001-i-want-to` | **Date**: 2025-10-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-i-want-to/spec.md`
**Constitution Version**: 1.1.0

## Summary

Build an AI-powered agent that automates job search outreach by discovering HR/recruiter contacts for given job postings and generating personalized connection messages. The agent uses Claude 3.5 Sonnet on Amazon Bedrock for reasoning and decision-making, Bedrock AgentCore for orchestration with Gateway (tool integration) and Memory primitives, and Python for backend logic. The system processes job posting inputs (company + title), autonomously searches for relevant HR contacts using web search tools, generates reasoning for contact selection, and outputs structured results with optional personalized outreach messages.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- boto3 (AWS SDK for Python)
- Amazon Bedrock AgentCore SDK
- pydantic (data validation)
- pytest (testing)
- python-dotenv (environment management)

**Storage**:
- Amazon S3 (job posting inputs, output results, logs)
- Optional: DynamoDB (contact caching via Memory primitive)

**Testing**: pytest with moto (AWS service mocking)

**Target Platform**: AWS cloud infrastructure (Lambda, Bedrock AgentCore, S3, CloudWatch)

**Project Type**: Single project with CLI interface and agent runtime

**Performance Goals**:
- Single job posting contact discovery: < 60 seconds
- Batch of 10 job postings: < 5 minutes
- Support 5 concurrent agent invocations during demo

**Constraints**:
- LLM must be hosted on AWS Bedrock (hackathon requirement)
- Must use at least one AgentCore primitive (Gateway required, Memory optional)
- All API keys in AWS Secrets Manager
- Respect third-party API rate limits
- Privacy-compliant (public data only)

**Scale/Scope**:
- MVP: 3-5 job postings per request
- Production: 10-50 job postings per batch
- Demo scenario: 5 concurrent users
- Expected agent lifecycle: <10 minutes per batch

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: User Story-First Development
✅ **PASS**: Feature spec defines 4 prioritized user stories (P1-P4), each independently testable with clear acceptance criteria.

### Principle II: Test-Driven Development (CONDITIONAL)
⚠️ **N/A**: Tests not explicitly requested in feature spec. Unit and integration tests will be included for quality but TDD workflow not enforced.

### Principle III: Constitution-Driven Planning
✅ **PASS**: This Constitution Check validates architecture decisions before research. Complexity Tracking table below documents any violations.

### Principle IV: Parallel-First Task Design
✅ **PASS**: Architecture supports parallel processing:
- Multiple job postings can be processed concurrently (Gateway tool invocations)
- User stories are independently implementable (P1 contact discovery → P2 reasoning → P3 batch → P4 messages)
- Models, services, and CLI can be developed in parallel

### Principle V: Explicit Path Conventions
✅ **PASS**: Single project structure follows convention with explicit paths documented below.

### Principle VI: Incremental Delivery & Checkpoints
✅ **PASS**: Implementation progresses through Setup → Foundational (AgentCore + Gateway) → P1 (basic discovery) → P2 (reasoning) → P3 (batch) → P4 (messages). Each checkpoint is independently validatable.

### Principle VII: Specification Completeness
✅ **PASS**: Feature spec has zero [NEEDS CLARIFICATION] markers, all requirements are testable, success criteria are measurable.

### Principle VIII: AWS AI Agent Compliance (NON-NEGOTIABLE)
✅ **PASS**: Architecture satisfies all requirements:
- ✅ LLM Hosting: Claude 3.5 Sonnet on Amazon Bedrock
- ✅ AWS Service Integration: Bedrock AgentCore with Gateway primitive (Memory optional)
- ✅ Reasoning LLMs: Claude Sonnet 4.5 for autonomous decision-making
- ✅ Autonomous Capabilities: Agent processes job postings without human intervention
- ✅ Tool Integration: Gateway connects to HR Lookup Tool (web search API wrapper)
- ✅ Deployment: AWS SAM or CDK for AgentCore deployment
- ✅ Third-Party Compliance: Web search via approved APIs (Tavily/Serper), secrets in Secrets Manager

**Gate Status**: ✅ ALL CHECKS PASSED - Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```
specs/001-i-want-to/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: Technology research and decisions
├── data-model.md        # Phase 1: Entity schemas and relationships
├── quickstart.md        # Phase 1: Local setup and demo guide
├── contracts/           # Phase 1: API and tool contracts
│   ├── agent-input.json       # AgentCore input schema
│   ├── agent-output.json      # AgentCore output schema
│   └── hr-lookup-tool.json    # Gateway tool contract
└── checklists/
    └── requirements.md  # Spec validation checklist
```

### Source Code (repository root)

```
src/
├── agent/
│   ├── __init__.py
│   ├── runtime.py           # AgentCore runtime initialization
│   ├── orchestrator.py      # Main agent orchestration logic
│   └── prompts.py           # Claude prompt templates
├── tools/
│   ├── __init__.py
│   ├── hr_lookup.py         # Gateway tool: HR contact discovery
│   ├── web_search.py        # Web search API integration (Tavily/Serper)
│   └── message_generator.py # Outreach message generation
├── models/
│   ├── __init__.py
│   ├── job_posting.py       # Job posting entity
│   ├── hr_contact.py        # HR contact entity
│   ├── search_result.py     # Contact discovery result
│   └── batch_job.py         # Batch processing entity
├── services/
│   ├── __init__.py
│   ├── contact_discovery.py # Contact discovery business logic
│   ├── reasoning_engine.py  # Contact selection reasoning
│   └── batch_processor.py   # Batch job orchestration
├── cli/
│   ├── __init__.py
│   └── main.py              # CLI entry point
└── utils/
    ├── __init__.py
    ├── aws_clients.py       # Boto3 client factories
    └── config.py            # Configuration management

infra/
├── cdk/
│   ├── app.py               # CDK app entry point
│   ├── agent_stack.py       # AgentCore infrastructure
│   └── tools_stack.py       # Lambda for HR Lookup Tool
└── sam-template.yaml        # Alternative SAM template

tests/
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_tools.py
├── integration/
│   ├── test_agent_runtime.py
│   └── test_batch_processing.py
└── fixtures/
    ├── mock_job_postings.json
    └── mock_hr_contacts.json

prompts/
├── contact_discovery.txt    # Prompt for finding HR contacts
├── contact_reasoning.txt    # Prompt for explaining selection
└── message_generation.txt   # Prompt for outreach messages

.env.example                 # Environment variable template
requirements.txt             # Python dependencies
pyproject.toml              # Poetry/setuptools config
Makefile                    # Deployment and testing commands
README.md                   # Project overview and quickstart
```

**Structure Decision**: Single project structure with clear separation of concerns:
- `src/agent/`: AgentCore runtime and orchestration
- `src/tools/`: Gateway tools registered with AgentCore
- `src/models/`: Pydantic data models for entities
- `src/services/`: Business logic for contact discovery and reasoning
- `src/cli/`: User interface for local testing
- `infra/`: Infrastructure as Code (CDK preferred for flexibility)
- `tests/`: Pytest test suite with unit and integration coverage
- `prompts/`: Versioned prompt templates for modularity

## Complexity Tracking

*No constitution violations. All principles satisfied by current architecture.*

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          User Input                             │
│                  (Job Postings: Company + Title)                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CLI / API Gateway                          │
│                  (src/cli/main.py)                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Bedrock AgentCore Runtime                     │
│                  (src/agent/runtime.py)                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         Claude 3.5 Sonnet (Bedrock)                        │ │
│  │  • Analyzes job posting context                            │ │
│  │  • Decides which tools to invoke                           │ │
│  │  • Generates reasoning for contact selection               │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │                                              │
│                   ▼                                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         AgentCore Gateway Primitive                        │ │
│  │         (Tool Integration)                                 │ │
│  └────────────────┬───────────────────────────────────────────┘ │
└───────────────────┼──────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     HR Lookup Tool                              │
│              (src/tools/hr_lookup.py)                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Web Search API (Tavily/Serper)                            │ │
│  │  • Search "[Company Name] HR recruiter [Job Title]"        │ │
│  │  • Parse LinkedIn profiles, company pages                  │ │
│  │  • Return candidate HR contacts                            │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│         Optional: Memory Primitive (DynamoDB)                   │
│         Cache discovered HR contacts for reuse                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                           │
│              (src/agent/orchestrator.py)                        │
│  • Aggregates tool results                                      │
│  • Invokes Claude for reasoning generation                      │
│  • Formats output (JSON/CSV)                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Output to S3 / CLI                          │
│  {                                                              │
│    "company": "TechCorp",                                       │
│    "job_title": "Senior Engineer",                             │
│    "hr_contact": {                                              │
│      "name": "Jane Doe",                                        │
│      "role": "Engineering Recruiter",                           │
│      "linkedin": "linkedin.com/in/janedoe",                     │
│      "reasoning": "Specializes in tech hiring, active posts"   │
│    }                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

## AWS Services Breakdown

### Core Services (Mandatory)

1. **Amazon Bedrock**
   - Model: Claude 3.5 Sonnet (claude-sonnet-4-5-20250929)
   - Purpose: Autonomous reasoning, contact selection, message generation
   - API: `bedrock-runtime.invoke_model()`

2. **Amazon Bedrock AgentCore**
   - Primitives: Gateway (tool integration), Memory (optional caching)
   - Purpose: Agent lifecycle management, tool orchestration
   - API: `agentcore.create_agent()`, `agentcore.invoke_agent()`

3. **AWS Lambda** (for HR Lookup Tool)
   - Runtime: Python 3.11
   - Purpose: Execute web search and contact extraction
   - Trigger: Synchronous invocation from AgentCore Gateway

4. **Amazon S3**
   - Buckets: `job-connector-inputs`, `job-connector-outputs`, `job-connector-logs`
   - Purpose: Input storage, result persistence, audit logging

5. **AWS Secrets Manager**
   - Secrets: `job-connector/web-search-api-key`
   - Purpose: Store Tavily/Serper API keys securely

6. **Amazon CloudWatch**
   - Logs: Agent runtime logs, Lambda logs, error tracking
   - Metrics: Invocation count, success rate, latency

### Optional Services (Future Enhancement)

- **Amazon DynamoDB**: Contact caching (Memory primitive backend)
- **Amazon SES**: Email sending for automated outreach (P4)
- **AWS Step Functions**: Complex batch job orchestration

## Technology Decisions

### LLM Selection: Claude 3.5 Sonnet

**Decision**: Use Claude 3.5 Sonnet (claude-sonnet-4-5-20250929) via Amazon Bedrock

**Rationale**:
- Strong multi-step reasoning for contact selection decisions
- Reliable structured output (JSON) for tool invocations
- Excellent at generating contextual reasoning explanations
- Native support for function calling (tool use)
- Available on AWS Bedrock (hackathon compliance)

**Alternatives Considered**:
- Amazon Nova: Newer but less proven for complex reasoning workflows
- Titan: Cost-effective but weaker reasoning capabilities

### Orchestration: Amazon Bedrock AgentCore

**Decision**: Use AgentCore with Gateway and Memory primitives

**Rationale**:
- Strongly recommended by hackathon guidelines (at least 1 primitive)
- Gateway primitive provides clean tool integration pattern
- Memory primitive enables contact caching without custom DB logic
- Built-in lifecycle management and error handling
- Native integration with Bedrock models

**Alternatives Considered**:
- Custom agentic loop with LangChain: More flexible but misses hackathon primitive requirement
- AWS Step Functions: Better for workflows but lacks AI reasoning integration

### Web Search: Tavily API

**Decision**: Use Tavily API for web search (Serper as fallback)

**Rationale**:
- Specialized for AI agent use cases (clean structured output)
- Good coverage of professional networks (LinkedIn, company sites)
- Rate limits suitable for demo (1000 searches/month on free tier)
- Simple REST API with JSON responses

**Alternatives Considered**:
- AWS Kendra: Requires indexed corpus, overkill for web search
- Google Custom Search: More complex setup, rate limit issues
- Direct web scraping: Legal/ethical concerns, fragile, rate-limited

### Deployment: AWS CDK

**Decision**: Use AWS CDK (Python) for infrastructure

**Rationale**:
- Type-safe infrastructure definitions
- Better composability than SAM for complex stacks
- Easier to integrate AgentCore constructs
- Local testing with `cdk synth`

**Alternatives Considered**:
- AWS SAM: Simpler but less flexible for AgentCore setup
- Terraform: Not AWS-native, steeper learning curve

## Phase 0 Research Summary

See [research.md](./research.md) for detailed findings. Key decisions:

1. **AgentCore Setup**: Use `boto3` with `agentcore` SDK, Gateway primitive for tool registration
2. **Prompt Engineering**: Structured prompts with JSON schema enforcement for reliable tool calls
3. **Contact Discovery Strategy**: Multi-stage search (LinkedIn → company website → general web) with confidence scoring
4. **Error Handling**: Graceful degradation when contacts not found, clear user messaging
5. **Rate Limiting**: Exponential backoff for API calls, queue-based batch processing

## Phase 1 Design Artifacts

### Data Models

See [data-model.md](./data-model.md) for complete schemas. Key entities:

- **JobPosting**: `company_name`, `job_title`, `description` (optional)
- **HRContact**: `name`, `role`, `company`, `profile_url`, `confidence_score`
- **SearchResult**: `job_posting`, `hr_contact`, `reasoning`, `timestamp`
- **BatchJob**: `id`, `job_postings[]`, `status`, `results[]`

### API Contracts

See [contracts/](./contracts/) for OpenAPI specs:

- **agent-input.json**: AgentCore invocation schema
- **agent-output.json**: Structured result format
- **hr-lookup-tool.json**: Gateway tool contract (input/output schemas)

### Quickstart Guide

See [quickstart.md](./quickstart.md) for:
- Local development setup
- Mock data testing
- AgentCore deployment steps
- Demo scenario walkthrough (< 10 minutes)

## Next Steps

1. **Run `/speckit.tasks`** to generate dependency-ordered task list
2. **Phase 2: Setup** - Initialize Python project, install dependencies, configure AWS credentials
3. **Phase 3: Foundational** - Implement AgentCore runtime, Gateway primitive, basic models
4. **Phase 4: User Story 1 (P1)** - Basic contact discovery (MVP)
5. **Phase 5: User Story 2 (P2)** - Intelligent reasoning generation
6. **Phase 6: User Story 3 (P3)** - Batch processing
7. **Phase 7: User Story 4 (P4)** - Message generation (optional)
8. **Phase 8: Polish** - Documentation, deployment automation, demo video

## Success Validation

Before declaring feature complete, verify against spec success criteria:
- [ ] SC-001: 80%+ contact discovery success rate
- [ ] SC-002: < 60 seconds per job posting
- [ ] SC-003: Batch of 10 in < 5 minutes
- [ ] SC-004: 90% reasoning rated "helpful"
- [ ] SC-005: 15+ minutes saved per posting (user survey)
- [ ] SC-006: 95% uptime during demo
- [ ] SC-007: Consistent output format
- [ ] SC-008: Clear, self-correcting error messages
- [ ] SC-009: 85% messages need minor customization (if P4 implemented)
- [ ] SC-010: < 40% message overlap (if P4 implemented)
