---
description: "Task list for AI Job Connector Agent implementation"
---

# Tasks: AI Job Connector Agent

**Input**: Design documents from `/specs/001-i-want-to/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, research.md, quickstart.md

**Tests**: Not explicitly requested in spec, so test tasks are excluded per constitution (Principle II: TDD is conditional)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root (per plan.md)
- Paths are absolute from repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure needed by all user stories

- [x] T001 Create Python project structure with directories: `src/agent/`, `src/tools/`, `src/models/`, `src/services/`, `src/cli/`, `src/utils/`, `infra/cdk/`, `tests/unit/`, `tests/integration/`, `tests/fixtures/`, `prompts/`
- [x] T002 Initialize Python 3.11+ virtual environment and create `requirements.txt` with dependencies: boto3, pydantic, pytest, python-dotenv, moto (AWS mocking)
- [x] T003 [P] Create `.env.example` file with environment variables: AWS_REGION, AWS_PROFILE, TAVILY_API_KEY, BEDROCK_MODEL_ID, AGENT_NAME
- [x] T004 [P] Create `pyproject.toml` with project metadata and Poetry/setuptools configuration
- [x] T005 [P] Create `Makefile` with commands for `make install`, `make test`, `make deploy`, `make clean`
- [x] T006 [P] Create `README.md` with project overview, quick start, and AWS hackathon compliance statement
- [x] T007 [P] Create `.gitignore` for Python (.venv, __pycache__, .env, *.pyc)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create `src/models/__init__.py` and define enums: ContactSource, BatchStatus, MessageTone, MessageChannel in `src/models/__init__.py`
- [ ] T009 [P] Create `src/models/job_posting.py` with JobPosting Pydantic model (company_name, job_title, description, job_url) per data-model.md
- [ ] T010 [P] Create `src/models/hr_contact.py` with HRContact Pydantic model (name, role, company, profile_url, source, confidence_score, additional_info) per data-model.md
- [ ] T011 [P] Create `src/models/search_result.py` with SearchResult Pydantic model (job_posting, hr_contact, reasoning, search_duration_seconds, timestamp, error_message, suggestions) per data-model.md
- [ ] T012 [P] Create `src/models/batch_job.py` with BatchJob Pydantic model (id, job_postings, status, results, created_at, started_at, completed_at, progress, error_count) per data-model.md
- [ ] T013 Create `src/utils/__init__.py` as empty init file
- [ ] T014 Create `src/utils/config.py` with configuration loader that reads from .env and validates required settings (AWS_REGION, BEDROCK_MODEL_ID)
- [ ] T015 Create `src/utils/aws_clients.py` with boto3 client factory functions: `get_bedrock_client()`, `get_bedrock_runtime_client()`, `get_s3_client()`, `get_secrets_manager_client()`
- [ ] T016 Create `src/agent/__init__.py` as empty init file
- [ ] T017 Create `src/agent/prompts.py` with prompt template constants: CONTACT_DISCOVERY_PROMPT, CONTACT_REASONING_PROMPT from prompts/ directory
- [ ] T018 Create `prompts/contact_discovery.txt` with Claude prompt for HR contact discovery (instruct to use hr_lookup tool, output JSON schema)
- [ ] T019 Create `prompts/contact_reasoning.txt` with Claude prompt for reasoning generation (explain contact selection in 2-3 sentences)
- [ ] T020 Create `src/agent/runtime.py` with AgentCore initialization: `initialize_agent()` function that creates Bedrock agent with Claude 3.5 Sonnet model
- [ ] T021 Create `src/tools/__init__.py` as empty init file
- [ ] T022 Create `src/tools/web_search.py` with Tavily API integration: `tavily_search(company_name, job_title, search_depth)` function that returns structured search results
- [ ] T023 Create `src/tools/hr_lookup.py` with Gateway tool implementation: `hr_lookup_tool(company_name, job_title)` that calls `web_search.py` and structures response per hr-lookup-tool.json contract
- [ ] T024 Create `src/agent/orchestrator.py` with core agent orchestration logic: `process_job_posting(job_posting)` function skeleton (to be filled in US1)
- [ ] T025 Create `src/services/__init__.py` as empty init file
- [ ] T026 Create `tests/fixtures/mock_job_postings.json` with 5 sample job postings for testing
- [ ] T027 Create `tests/fixtures/mock_hr_contacts.json` with 5 sample HR contact responses for testing
- [ ] T028 Create `infra/cdk/app.py` CDK app entry point with AgentCore stack reference
- [ ] T029 Create `infra/cdk/agent_stack.py` with AgentCore infrastructure: agent definition, IAM roles, S3 buckets (job-connector-inputs, job-connector-outputs, job-connector-logs)
- [ ] T030 Create `infra/cdk/tools_stack.py` with Lambda function for HR Lookup Tool (Python 3.11 runtime, environment variables for Tavily API key)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Contact Discovery (Priority: P1) 🎯 MVP

**Goal**: Given 3-5 job postings, return HR contact information (name, role, reasoning) for each

**Independent Test**: Submit 3-5 job postings (company + title) and verify agent returns contact information (name, role, reasoning) for each. Success means user has actionable contact data.

### Implementation for User Story 1

- [ ] T031 [US1] Implement `src/services/contact_discovery.py` with `discover_contact(job_posting: JobPosting) -> SearchResult` function that orchestrates HR lookup
- [ ] T032 [US1] Update `src/agent/orchestrator.py` `process_job_posting()` to:
  1. Parse JobPosting input
  2. Invoke AgentCore with contact_discovery prompt
  3. Call hr_lookup tool via Gateway primitive
  4. Collect tool result and create SearchResult
  5. Return structured SearchResult
- [ ] T033 [US1] Update `src/tools/hr_lookup.py` to handle edge cases:
  - No contact found → return empty contacts list with suggestions
  - Ambiguous company name → use first match with warning in reasoning
  - Rate limit hit → return error with retry_after_seconds
- [ ] T034 [US1] Create `src/cli/__init__.py` as empty init file
- [ ] T035 [US1] Create `src/cli/main.py` with CLI entry point:
  - Subcommand `process` for single job posting: `--company "Name" --title "Role"`
  - Parse arguments and call `contact_discovery.discover_contact()`
  - Output SearchResult as formatted JSON to stdout
- [ ] T036 [US1] Update `src/agent/orchestrator.py` to handle errors gracefully:
  - Catch API exceptions (RateLimitError, NoContactFoundError)
  - Populate SearchResult.error_message and suggestions fields
  - Ensure SearchResult always returned even on failures
- [ ] T037 [US1] Add input validation in `src/services/contact_discovery.py`:
  - Validate JobPosting has non-empty company_name and job_title
  - Return clear error message for malformed input (FR-006)
- [ ] T038 [US1] Test end-to-end flow with mock data:
  - Run `python -m src.cli.main process --company "Anthropic" --title "AI Safety Researcher"` with mock hr_lookup responses
  - Verify output matches SearchResult schema from data-model.md
  - Verify reasoning field is populated (10-1000 chars)

**Checkpoint**: At this point, User Story 1 (MVP) should be fully functional and testable independently. User can discover HR contacts for 3-5 job postings via CLI.

---

## Phase 4: User Story 2 - Intelligent Contact Reasoning (Priority: P2)

**Goal**: Explain WHY each HR contact was selected with unique, contextual reasoning

**Independent Test**: Submit job postings and examine reasoning field for each contact. Success means each reasoning explanation is unique, contextual, and helps user understand match quality.

### Implementation for User Story 2

- [ ] T039 [US2] Create `src/services/reasoning_engine.py` with `generate_reasoning(job_posting: JobPosting, hr_contact: HRContact, search_context: dict) -> str` function
- [ ] T040 [US2] Update `src/agent/orchestrator.py` `process_job_posting()` to:
  - After receiving hr_contact from Gateway tool, invoke Claude again with contact_reasoning prompt
  - Pass job_posting context, discovered hr_contact, and search metadata (source, confidence, additional_info)
  - Extract reasoning text from Claude response (2-3 sentences, specific and actionable)
- [ ] T041 [US2] Implement reasoning logic in `src/services/reasoning_engine.py`:
  - Analyze company type (startup vs enterprise) based on search results
  - Prioritize department-specific recruiters (engineering recruiter for tech roles)
  - Highlight recent activity (LinkedIn posts) if available in additional_info
  - Explain confidence score context (high confidence = LinkedIn + exact match, low = inferred)
- [ ] T042 [US2] Update `prompts/contact_reasoning.txt` to enforce reasoning quality:
  - Must explain WHY this specific person (role specialization, recent activity)
  - Must address company context (startup founders vs enterprise recruiters)
  - Must be transparent about uncertainty if low confidence
  - Must be 2-3 sentences, no generic statements
- [ ] T043 [US2] Update `src/tools/hr_lookup.py` to enrich additional_info field:
  - Extract recent activity from search results (e.g., "Posted about hiring 2 weeks ago")
  - Identify department from role title (e.g., "Engineering" from "Engineering Recruiter")
  - Add metadata to HRContact.additional_info dict
- [ ] T044 [US2] Handle edge cases in `src/services/reasoning_engine.py`:
  - Multiple candidates exist → explain why this one selected (most recent, department match)
  - Niche role (AI Safety Researcher) → explain specialized match (CTO with AI background)
  - Limited info → be transparent ("Inferred from company size and typical org structure")
  - No contact found → explain why and suggest alternatives
- [ ] T045 [US2] Update CLI output in `src/cli/main.py`:
  - Pretty-print reasoning with highlighting
  - Show confidence score interpretation (0.9+ = "High confidence", etc.)
- [ ] T046 [US2] Test reasoning quality:
  - Run with 5 different job types (tech, product, niche research, startup, enterprise)
  - Verify each reasoning is unique and contextual (no repeated templates)
  - Verify reasoning addresses role specificity and company context

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Reasoning field provides valuable context for each contact.

---

## Phase 5: User Story 3 - Batch Processing and Output Management (Priority: P3)

**Goal**: Process 10-50 job postings in batch with progress tracking and exportable results (CSV/JSON)

**Independent Test**: Submit 20 job postings and verify all processed within 5 minutes with structured output (CSV or JSON). Success means user can use data in CRM tool.

### Implementation for User Story 3

- [ ] T047 [P] [US3] Create `src/services/batch_processor.py` with `BatchProcessor` class:
  - `process_batch(batch_job: BatchJob, max_concurrent: int = 3) -> BatchJob` function
  - Use asyncio for concurrent processing with Semaphore for rate limiting
  - Update BatchJob.status, progress, error_count as processing proceeds
- [ ] T048 [P] [US3] Create `src/utils/formatters.py` with export functions:
  - `export_to_json(batch_job: BatchJob, output_path: str)` - serialize BatchJob to JSON
  - `export_to_csv(batch_job: BatchJob, output_path: str)` - flatten SearchResults to CSV rows
  - `export_summary_text(batch_job: BatchJob, output_path: str)` - human-readable summary
- [ ] T049 [US3] Update `src/cli/main.py` with `batch` subcommand:
  - `--input <file>` flag for JSON file with job_postings array
  - `--output <file>` flag for output file path
  - `--format {json,csv}` flag for output format (default: json)
  - `--max-concurrent <n>` flag for concurrency control (default: 3)
- [ ] T050 [US3] Implement progress tracking in `src/services/batch_processor.py`:
  - Print "Processing 1/20", "Processing 2/20", etc. to stdout
  - Update BatchJob.progress after each job posting completes
  - Calculate and display ETA based on average processing time
- [ ] T051 [US3] Implement error handling in `src/services/batch_processor.py`:
  - Failed job postings don't block others (independent processing)
  - Track failures in BatchJob.error_count
  - Set BatchJob.status to PARTIALLY_COMPLETED if some fail, COMPLETED if all succeed, FAILED if all fail
  - Include failed postings in output with error_message and suggestions fields
- [ ] T052 [US3] Add rate limiting logic in `src/services/batch_processor.py`:
  - Limit concurrent searches to max_concurrent (default 3)
  - Add 500ms delay between requests (per research.md)
  - Exponential backoff on rate limit errors (1s → 2s → 4s)
  - Fallback to Serper if Tavily quota exhausted
- [ ] T053 [US3] Implement CSV export in `src/utils/formatters.py`:
  - Columns: company_name, job_title, hr_name, hr_role, hr_profile_url, confidence_score, reasoning, status (success/failure)
  - Handle None values for hr_contact (no contact found cases)
  - Include summary row at end: total postings, successful, failed, avg confidence
- [ ] T054 [US3] Implement JSON export in `src/utils/formatters.py`:
  - Full BatchJob serialization with metadata (batch_id, status, summary stats)
  - Include created_at, started_at, completed_at timestamps
  - Summary section: total_postings, successful_discoveries, failed_discoveries, average_confidence, total_duration_seconds
- [ ] T055 [US3] Add batch validation in `src/cli/main.py`:
  - Check input file exists and is valid JSON
  - Validate job_postings array contains 1-50 entries (per data-model.md)
  - Validate each JobPosting has required fields (company_name, job_title)
  - Exit with clear error if validation fails
- [ ] T056 [US3] Test batch processing:
  - Create `tests/fixtures/batch_20_jobs.json` with 20 diverse job postings
  - Run `python -m src.cli.main batch --input tests/fixtures/batch_20_jobs.json --output results.json`
  - Verify completes in < 5 minutes (SC-003)
  - Verify JSON output matches agent-output.json schema
  - Export to CSV and verify format is correct

**Checkpoint**: At this point, all three core user stories (US1, US2, US3) should be independently functional. Users can process large batches with progress tracking and export.

---

## Phase 6: User Story 4 - Personalized Outreach Message Generation (Priority: P4)

**Goal**: Generate unique, personalized LinkedIn/email messages for each discovered HR contact

**Independent Test**: Request message generation for discovered contacts. Success means each message is unique, includes context (job, company, contact), and needs minimal customization.

### Implementation for User Story 4

- [ ] T057 [P] [US4] Create `src/models/outreach_message.py` with OutreachMessage Pydantic model (hr_contact, job_posting, subject, body, tone, channel, generated_at, personalization_notes) per data-model.md
- [ ] T058 [P] [US4] Create `prompts/message_generation.txt` with Claude prompt for outreach message generation (personalize based on role, company, and contact, keep under 200 words)
- [ ] T059 [US4] Create `src/tools/message_generator.py` with `generate_outreach_message(search_result: SearchResult, tone: MessageTone, channel: MessageChannel) -> OutreachMessage` function
- [ ] T060 [US4] Implement message generation logic in `src/tools/message_generator.py`:
  - Invoke Claude with message_generation prompt
  - Pass job_posting, hr_contact, and tone/channel preferences
  - Extract subject and body from Claude response
  - Ensure uniqueness (< 40% overlap between messages per SC-010)
  - Add personalization_notes explaining what was customized
- [ ] T061 [US4] Update `src/cli/main.py` `batch` subcommand to support message generation:
  - `--generate-messages` flag to enable message generation
  - `--tone {professional,friendly,formal,enthusiastic}` flag for message tone (default: professional)
  - `--channel {linkedin,email,generic}` flag for delivery channel (default: linkedin)
- [ ] T062 [US4] Update `src/services/batch_processor.py` to optionally generate messages:
  - If `include_messages=True`, call `message_generator.generate_outreach_message()` after contact discovery
  - Add OutreachMessage to SearchResult (extend data model with optional outreach_message field)
  - Include messages in batch output (JSON/CSV)
- [ ] T063 [US4] Implement message quality checks in `src/tools/message_generator.py`:
  - Subject: 5-200 chars, mentions company and role
  - Body: 50-2000 chars, includes call-to-action
  - Tone matches requested style (professional = formal language, friendly = conversational)
  - No generic templates ("I am writing to express interest...") - must be personalized
- [ ] T064 [US4] Handle edge cases in `src/tools/message_generator.py`:
  - Limited contact info → create respectful introduction without assumptions
  - Niche roles → adjust technical depth (AI Safety = mention ML safety experience)
  - Different channels → format appropriately (LinkedIn = shorter, email = can be longer with formatting)
- [ ] T065 [US4] Update CSV export in `src/utils/formatters.py`:
  - Add columns: message_subject, message_body (if messages generated)
  - Escape quotes and newlines properly for CSV format
- [ ] T066 [US4] Test message generation:
  - Generate messages for 10 different contacts with various roles and companies
  - Verify each message is unique (calculate overlap %, should be < 40%)
  - Verify messages are professional and concise (under 200 words)
  - Verify call-to-action is present in each message

**Checkpoint**: All user stories (US1, US2, US3, US4) should now be independently functional. Full feature set complete.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and deployment readiness

- [ ] T067 [P] Add comprehensive error handling across all services:
  - Wrap all AWS API calls in try/except with specific exception types
  - Log errors to CloudWatch with context (batch_id, job_posting_id)
  - Return user-friendly error messages (not raw exceptions)
- [ ] T068 [P] Add logging infrastructure:
  - Create `src/utils/logger.py` with configured Python logging
  - Log to both stdout (for CLI) and file (agent_execution.log)
  - Include log levels: INFO for progress, WARNING for rate limits, ERROR for failures
  - Upload logs to S3 `job-connector-logs/{batch_id}/` after batch completes
- [ ] T069 [P] Create deployment automation:
  - Update `Makefile` with `make deploy` command that runs `cdk deploy`
  - Add `make destroy` command for cleanup
  - Add `make logs` command to tail CloudWatch logs
- [ ] T070 [P] Create AWS Secrets Manager integration:
  - Update `src/utils/config.py` to fetch Tavily API key from Secrets Manager
  - Create secret `job-connector/web-search-api-key` during CDK deploy
  - Handle secret rotation gracefully (refresh on 403 errors)
- [ ] T071 [P] Add CloudWatch metrics:
  - Instrument `src/services/batch_processor.py` with custom metrics
  - Track: invocation_count, success_rate, average_latency, error_count
  - Create CloudWatch dashboard in CDK stack
- [ ] T072 [P] Optimize performance:
  - Implement contact caching in `src/tools/hr_lookup.py` (optional DynamoDB Memory primitive)
  - Add cache hit/miss tracking in logs
  - Add `--use-cache` flag to CLI
- [ ] T073 Update `README.md` with complete documentation:
  - Architecture diagram (ASCII art from plan.md)
  - Quick start guide (< 10 min setup from quickstart.md)
  - CLI usage examples for all subcommands
  - Troubleshooting section
  - AWS hackathon compliance statement
- [ ] T074 Create demo script:
  - `demo.sh` that runs end-to-end demo with sample data
  - Shows: single posting → batch of 5 → batch with messages → CSV export
  - Outputs to `demo-results/` directory
  - Takes < 3 minutes to run with mock data
- [ ] T075 [P] Add input/output examples:
  - Create `examples/input_single.json` for single job posting
  - Create `examples/input_batch.json` for batch of 10 job postings
  - Create `examples/output_results.json` showing expected output format
  - Create `examples/output_results.csv` showing CSV export format
- [ ] T076 Run quickstart validation from quickstart.md:
  - Verify all setup steps work (< 10 min from clone to demo)
  - Verify mock demo runs successfully
  - Verify real API integration works (if Tavily key provided)
  - Fix any issues found in quickstart instructions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T007) - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion (T008-T030)
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion (T031-T038) - Extends reasoning functionality
- **User Story 3 (Phase 5)**: Depends on User Story 1 completion (T031-T038) - Can develop in parallel with US2
- **User Story 4 (Phase 6)**: Depends on User Story 1 completion (T031-T038) - Can develop in parallel with US2/US3
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Extends US1 reasoning - Depends on T031-T038 (US1 implementation)
- **User Story 3 (P3)**: Adds batch processing - Depends on T031-T038 (US1 implementation), can develop in parallel with US2
- **User Story 4 (P4)**: Adds messages - Depends on T031-T038 (US1 implementation), can develop in parallel with US2/US3

### Within Each User Story

**User Story 1 (Basic Contact Discovery)**:
- T031 (contact_discovery service) before T032 (orchestrator update)
- T033 (hr_lookup edge cases) can be parallel with T032
- T034-T035 (CLI) after T031-T032 (core logic)
- T036-T037 (error handling, validation) after T035 (CLI)
- T038 (end-to-end test) last

**User Story 2 (Intelligent Reasoning)**:
- T039 (reasoning_engine) can start immediately after US1
- T040 (orchestrator update) after T039
- T041 (reasoning logic) after T039
- T042 (prompt update) parallel with T041
- T043 (hr_lookup enrichment) parallel with T041
- T044 (edge cases) after T041
- T045 (CLI output) after T044
- T046 (test) last

**User Story 3 (Batch Processing)**:
- T047 (batch_processor) and T048 (formatters) can run in parallel
- T049 (CLI batch command) after T047
- T050-T052 (progress, errors, rate limiting) after T047
- T053-T054 (CSV/JSON export) extend T048
- T055 (validation) parallel with T050-T054
- T056 (test) last

**User Story 4 (Message Generation)**:
- T057 (OutreachMessage model) and T058 (prompt) can run in parallel
- T059 (message_generator) after T057-T058
- T060 (generation logic) after T059
- T061 (CLI flags) parallel with T060
- T062 (batch_processor update) after T060-T061
- T063-T064 (quality checks, edge cases) after T060
- T065 (CSV export update) after T063-T064
- T066 (test) last

### Parallel Opportunities

**Setup Phase (all tasks marked [P] can run in parallel)**:
- T003, T004, T005, T006, T007 (all config files)

**Foundational Phase (some tasks marked [P] can run in parallel)**:
- T009, T010, T011, T012 (all model files - different files)
- T018, T019 (prompt files - different files)

**User Story 1**:
- T033 parallel with T032
- T036 and T037 parallel

**User Story 2**:
- T042 parallel with T041
- T043 parallel with T041

**User Story 3**:
- T047 and T048 parallel (different files)
- T050, T051, T052 parallel (all update batch_processor.py but different functions)
- T053 and T054 parallel (different functions in formatters.py)
- T055 parallel with T050-T054

**User Story 4**:
- T057 and T058 parallel (different files)
- T061 parallel with T060
- T063 and T064 parallel (different functions)

**Polish Phase (most tasks marked [P] can run in parallel)**:
- T067, T068, T069, T070, T071, T072 (all different files/services)
- T075 parallel with T073-T074

**Cross-Story Parallelism**:
- After US1 complete, US2, US3, and US4 can be developed in parallel by different team members

---

## Parallel Execution Examples

### User Story 1 (Basic Contact Discovery)

```bash
# After Foundational phase completes, launch US1 tasks:
# These can be worked on concurrently:
Task T033: "Update hr_lookup.py edge cases"
Task T036: "Add error handling to orchestrator"
Task T037: "Add input validation to contact_discovery"

# Then sequentially:
Task T035: "Create CLI main.py" (after T031-T034)
Task T038: "Test end-to-end flow" (after all)
```

### User Story 3 (Batch Processing)

```bash
# These can be launched together:
Task T047: "Create batch_processor.py"
Task T048: "Create formatters.py"

# Then these can run in parallel:
Task T050: "Implement progress tracking"
Task T051: "Implement error handling"
Task T052: "Add rate limiting"
Task T053: "Implement CSV export"
Task T054: "Implement JSON export"
Task T055: "Add batch validation"

# Finally:
Task T056: "Test batch processing" (after all)
```

### Polish Phase

```bash
# All these can run concurrently:
Task T067: "Error handling"
Task T068: "Logging infrastructure"
Task T069: "Deployment automation"
Task T070: "Secrets Manager integration"
Task T071: "CloudWatch metrics"
Task T072: "Performance optimization"
Task T075: "Input/output examples"

# Then:
Task T073: "Update README"
Task T074: "Create demo script"
Task T076: "Run quickstart validation"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T030) - CRITICAL blocking phase
3. Complete Phase 3: User Story 1 (T031-T038)
4. **STOP and VALIDATE**: Test User Story 1 independently with 5 job postings
5. Deploy to AWS and run hackathon demo (if US1 works, you have a viable submission)

**Estimated Time**: ~8-12 hours for MVP (US1 only)

**Demo-Ready Checkpoint**: After T038, you can demonstrate:
- Input: 5 job postings → Output: 5 HR contacts with reasoning
- Success criteria: 80%+ success rate, < 60s per posting
- AWS compliance: Bedrock + AgentCore + Gateway primitive ✅

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T030)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!) (T031-T038)
3. Add User Story 2 → Test independently → Deploy/Demo (T039-T046)
4. Add User Story 3 → Test independently → Deploy/Demo (T047-T056)
5. Add User Story 4 → Test independently → Deploy/Demo (T057-T066)
6. Polish & Integration → Final release (T067-T076)

**Estimated Time**: ~20-30 hours for full feature set (all 4 user stories)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T030)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T031-T038) - Priority 1 (MUST COMPLETE FIRST)
   - **Developer B**: User Story 2 (T039-T046) after Developer A finishes US1
   - **Developer C**: User Story 3 (T047-T056) after Developer A finishes US1
   - **Developer D**: User Story 4 (T057-T066) after Developer A finishes US1
3. Once US1 is complete, US2/US3/US4 can proceed in parallel
4. All developers merge to main and do Polish phase together (T067-T076)

**Critical Path**: Foundational (T008-T030) → US1 (T031-T038) → Parallel stories → Polish

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] labels** (US1, US2, US3, US4) map task to specific user story for traceability
- **Each user story should be independently completable and testable**
- **No test tasks included** - Tests not explicitly requested in spec (per Principle II: TDD is conditional)
- **Commit after each task or logical group**
- **Stop at any checkpoint to validate story independently**
- **AWS compliance is non-negotiable** (Principle VIII) - Foundational phase ensures this
- **Parallel opportunities identified** with [P] markers for optimal team collaboration
- **Avoid**: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Count Summary

- **Total Tasks**: 76
- **Phase 1 (Setup)**: 7 tasks
- **Phase 2 (Foundational)**: 23 tasks (BLOCKING)
- **Phase 3 (User Story 1 - P1)**: 8 tasks (MVP)
- **Phase 4 (User Story 2 - P2)**: 8 tasks
- **Phase 5 (User Story 3 - P3)**: 10 tasks
- **Phase 6 (User Story 4 - P4)**: 10 tasks
- **Phase 7 (Polish)**: 10 tasks

**Minimum Viable Demo**: Setup (7) + Foundational (23) + US1 (8) = **38 tasks for MVP**

**Full Feature Set**: All 76 tasks

**Parallel Opportunities**: ~35 tasks can be parallelized across the project
