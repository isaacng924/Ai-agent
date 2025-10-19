<!--
Sync Impact Report:
- Version: 1.0.0 → 1.1.0 (MINOR bump)
- Modified principles:
  * VII. Specification Completeness - No changes
- Added sections:
  * VIII. AWS AI Agent Compliance (NEW principle)
  * Project Mission section (NEW)
  * AWS Hackathon Requirements section (expanded)
- Removed sections: None
- Templates requiring updates:
  ✅ plan-template.md - Constitution Check must now verify AWS compliance requirements
  ✅ spec-template.md - Already supports compliance checks
  ✅ tasks-template.md - Already supports infrastructure and integration tasks
- Follow-up TODOs: None
-->

# AI Job Connector Agent Constitution

## Project Mission

**Project Name**: AI Job Connector Agent

**Purpose**: Automate job search outreach by intelligently finding HR/recruiter contacts for specified job titles and companies, then generating personalized connection messages.

**Core Value Proposition**: Transform manual, time-consuming job networking into an autonomous AI-driven process that increases outreach volume while maintaining personalization quality.

**Target Platform**: AWS cloud infrastructure (AWS Bedrock, Lambda, DynamoDB, etc.)

**Hackathon Context**: AWS AI Agent Hackathon submission demonstrating autonomous AI capabilities with LLM reasoning, external tool integration (LinkedIn/web search), and personalized content generation.

## Core Principles

### I. User Story-First Development

Every feature begins with prioritized, independently testable user stories (P1, P2, P3...). Each user story must:
- Deliver standalone value as an MVP increment
- Be implementable, testable, and deployable independently
- Have clear acceptance criteria in Given/When/Then format
- Include priority justification explaining user value

**Rationale**: Enables incremental delivery, parallel development, and ensures every implementation delivers measurable user value. Prevents building features that don't serve user needs.

### II. Test-Driven Development (CONDITIONAL)

When tests are explicitly requested in the feature specification:
- Tests MUST be written before implementation code
- Tests MUST fail initially (Red phase)
- Implementation proceeds only after test approval (Green phase)
- Refactoring follows successful tests (Refactor phase)

When tests are NOT requested, this principle does not apply.

**Rationale**: Ensures code correctness, prevents regression, and provides living documentation. The conditional nature respects project constraints while maintaining quality when testing is required.

### III. Constitution-Driven Planning

All implementation plans must pass the Constitution Check gate:
- Verified before Phase 0 research begins
- Re-verified after Phase 1 design completes
- Any principle violations must be documented in Complexity Tracking table
- Simpler alternatives must be evaluated and justified if rejected

**Rationale**: Prevents scope creep, enforces simplicity-first thinking, and ensures architectural decisions are deliberate and documented.

### IV. Parallel-First Task Design

Tasks must be designed for maximum parallelization:
- Mark [P] for tasks with no file conflicts or dependencies
- Group by user story for independent story-level parallelism
- Foundational phase blocks all stories but internal tasks can be parallel
- Different team members can work on different stories simultaneously

**Rationale**: Reduces time-to-delivery, enables efficient team collaboration, and prevents bottlenecks in the development workflow.

### V. Explicit Path Conventions

Code must follow consistent, documented path conventions:
- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- All tasks must specify exact file paths
- Structure must be documented in plan.md

**Rationale**: Eliminates ambiguity, enables accurate dependency analysis, and facilitates code navigation for both humans and AI agents.

### VI. Incremental Delivery & Checkpoints

Implementation must proceed through validated checkpoints:
- Setup → Foundational → User Story 1 (MVP) → Story 2 → Story 3...
- Each checkpoint must include independent validation
- Stop and validate before proceeding to next story
- Each story addition must not break previous stories

**Rationale**: Enables early feedback, reduces risk, allows partial deployment, and ensures continuous value delivery throughout development.

### VII. Specification Completeness

Feature specifications must be complete before planning:
- All NEEDS CLARIFICATION markers must be resolved
- Edge cases must be documented
- Functional requirements must be specific and measurable
- Success criteria must be technology-agnostic and testable

**Rationale**: Prevents mid-implementation scope changes, reduces rework, and ensures all stakeholders have shared understanding before code is written.

### VIII. AWS AI Agent Compliance (NON-NEGOTIABLE)

All implementations MUST satisfy AWS Hackathon AI Agent requirements:

**LLM Hosting (MANDATORY)**:
- LLM MUST be hosted on AWS Bedrock or Amazon SageMaker AI
- No external LLM services (OpenAI, Anthropic direct, etc.) for primary agent logic

**AWS Service Integration (AT LEAST ONE REQUIRED)**:
- Amazon Bedrock AgentCore with at least 1 primitive (strongly recommended)
- Amazon Bedrock / Nova models
- Amazon Q for knowledge integration
- Amazon SageMaker AI for custom models
- AWS SDKs for Agents / Nova Act SDK
- AWS Transform for data processing
- Kiro for agent orchestration

**AI Agent Qualification (ALL THREE REQUIRED)**:
1. **Reasoning LLMs**: Uses LLM or similar component for autonomous decision-making
2. **Autonomous Capabilities**: Demonstrates task execution with or without human input
3. **Tool Integration**: Integrates APIs, databases, external tools (web search, LinkedIn API, email generation) or other agents

**Deployment & Functionality**:
- Project MUST install and run consistently on AWS infrastructure
- Must function as depicted in demo video and documentation
- Must include deployment automation (CloudFormation, CDK, or Terraform)

**Third-Party Integration Compliance**:
- LinkedIn API usage MUST comply with LinkedIn Developer Agreement
- Web scraping MUST respect robots.txt and rate limits
- Email generation MUST comply with anti-spam regulations (CAN-SPAM, GDPR)
- All API keys MUST be stored in AWS Secrets Manager or Parameter Store

**Rationale**: Ensures hackathon submission eligibility, prevents disqualification, and guarantees the project meets AWS's definition of an AI agent. Non-compliance blocks demo submission.

## Quality Standards

### Documentation Requirements

- Every feature must have spec.md, plan.md, and tasks.md
- Quickstart.md must be created in Phase 1 with runnable examples
- Data models must be documented before implementation
- Contract specifications must precede endpoint implementation
- All MUST/SHOULD language must be RFC 2119 compliant
- AWS service architecture diagrams must be included in plan.md
- Third-party API compliance documentation must be in contracts/

### Code Organization

- Follow the path conventions defined in Principle V
- Models before services, services before endpoints/CLI
- Shared infrastructure in Foundational phase
- Feature-specific code in user story phases
- Cross-cutting concerns in final Polish phase
- AWS infrastructure code in `infra/` directory (CloudFormation/CDK/Terraform)
- Lambda functions in `src/lambdas/` with clear entry points

### AWS Hackathon Requirements

**Mandatory Compliance Checklist** (verify before submission):
- [ ] LLM hosted on AWS Bedrock or SageMaker AI
- [ ] Uses at least one required AWS service (Bedrock AgentCore preferred)
- [ ] Implements reasoning LLM for decision-making
- [ ] Demonstrates autonomous task execution
- [ ] Integrates external tools (LinkedIn, web search, email)
- [ ] Includes working deployment automation
- [ ] Functions as documented in demo video
- [ ] Third-party API usage is compliant and authorized
- [ ] All secrets stored in AWS Secrets Manager
- [ ] README explains significant hackathon-period updates

**Project-Specific Requirements**:
- Contact discovery must use web search APIs (Tavily, Serper, or AWS Kendra)
- LinkedIn integration must use official LinkedIn API or compliant scraping
- Message generation must use AWS Bedrock LLM (Nova preferred)
- Contact data storage must use DynamoDB or RDS
- Email delivery must use Amazon SES
- Rate limiting must prevent API abuse
- Privacy compliance for contact data handling

**Demo Requirements**:
- Video must show end-to-end workflow: input → search → contact discovery → message generation
- Must demonstrate autonomous decision-making (which contacts to prioritize, message tone selection)
- Must show AWS service integration visibly (Bedrock API calls, DynamoDB queries, etc.)
- Quickstart must enable judges to run demo in <10 minutes

## Development Workflow

### Feature Lifecycle

1. **Specification** (`/speckit.specify`): Create spec.md with prioritized user stories
2. **Clarification** (`/speckit.clarify`): Resolve underspecified areas
3. **Planning** (`/speckit.plan`): Generate implementation plan with research
4. **Analysis** (`/speckit.analyze`): Verify cross-artifact consistency
5. **Task Generation** (`/speckit.tasks`): Create dependency-ordered tasks
6. **Implementation** (`/speckit.implement`): Execute task list
7. **Validation**: Verify against checklist (`/speckit.checklist`)

### Review & Approval Gates

- Spec must be approved before planning begins
- Constitution Check must pass before Phase 0 research (including AWS compliance)
- Tests (if required) must fail before implementation
- Each user story must validate independently at checkpoint
- Final validation against success criteria before feature complete
- AWS compliance checklist must be verified before hackathon submission

### Continuous Improvement

- Constitution can be amended via `/speckit.constitution`
- Amendments require documentation of changed principles
- Version must increment per semantic versioning rules
- All dependent templates must be synchronized on amendment

## Governance

### Amendment Process

1. Propose amendment with rationale
2. Execute `/speckit.constitution` command
3. Review Sync Impact Report for affected templates
4. Update all flagged templates for consistency
5. Commit with message: `docs: amend constitution to vX.Y.Z (summary)`

### Versioning Policy

- **MAJOR**: Principle removal, redefinition, or backward-incompatible governance change
- **MINOR**: New principle added or existing principle materially expanded
- **PATCH**: Clarifications, wording improvements, typo fixes without semantic changes

### Compliance Verification

- All feature specifications must reference constitution version
- Implementation plans must include Constitution Check section with AWS compliance
- Task lists must reflect principle-driven organization (by user story)
- Code reviews must verify path convention compliance
- Post-implementation analysis must validate against all applicable principles
- Pre-submission review must verify all AWS hackathon requirements

### Flexibility Clause

In hackathon or time-constrained contexts:
- Complexity Tracking table justifies temporary violations
- Violations must document why simpler alternatives are insufficient
- Technical debt must be tracked for post-hackathon remediation
- Constitution compliance may be relaxed for throwaway prototypes but MUST be enforced for production code
- **EXCEPTION**: AWS AI Agent Compliance (Principle VIII) is NON-NEGOTIABLE even in time constraints

**Version**: 1.1.0 | **Ratified**: 2025-10-12 | **Last Amended**: 2025-10-12
