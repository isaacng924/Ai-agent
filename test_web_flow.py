"""Test the full web flow without Streamlit."""

import logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

from src.services.cv_parser import CVParser
from src.models.job_posting import JobPosting
from src.models.batch_job import BatchJob
from src.agent.runtime import AgentRuntime
from src.agent.orchestrator import process_batch_job

print("=" * 70)
print("Testing Full Web Flow (without Streamlit UI)")
print("=" * 70)

# Step 1: Parse CV
print("\n1. Parsing CV...")
parser = CVParser()
cv_profile = parser.parse_file("test_cv_simple.txt")
print(f"✓ CV Parsed: {cv_profile.full_name}")

# Step 2: Create job postings
print("\n2. Creating job postings...")
job_postings = [
    JobPosting(
        company_name="Google",
        job_title="Software Engineer",
    ),
]
print(f"✓ Created {len(job_postings)} job posting(s)")

# Step 3: Create batch job
print("\n3. Creating batch job...")
batch_job = BatchJob(job_postings=job_postings)
print(f"✓ Batch job ID: {batch_job.id}")

# Step 4: Initialize runtime
print("\n4. Initializing agent runtime...")
agent_runtime = AgentRuntime()
print("✓ Runtime initialized")

# Step 5: Process batch with CV profile
print("\n5. Processing batch job with CV profile...")
print("   (This will take 15-30 seconds per job)")
print("   - Finding HR contacts")
print("   - Generating personalized messages")
print()

def progress_callback(current, total, result):
    print(f"   [{current}/{total}] {result.job_posting.company_name}: ", end="")
    if result.hr_contact:
        print(f"✓ Found {result.hr_contact.name}")
        if result.outreach_message:
            print(f"      ✓ Message generated ({len(result.outreach_message)} chars)")
        else:
            print(f"      ✗ No message generated")
    else:
        print("✗ No contact found")

batch_job = process_batch_job(
    batch_job=batch_job,
    agent_runtime=agent_runtime,
    progress_callback=progress_callback,
    cv_profile=cv_profile,
    message_tone="professional",
    message_channel="linkedin",
    message_length="medium",
)

# Step 6: Display results
print("\n" + "=" * 70)
print("Results Summary")
print("=" * 70)
print(f"Status: {batch_job.status.value}")
print(f"Total jobs: {len(batch_job.job_postings)}")
print(f"Successful: {len(batch_job.results) - batch_job.error_count}")
print(f"Failed: {batch_job.error_count}")

print("\n" + "=" * 70)
print("Detailed Results")
print("=" * 70)

for idx, result in enumerate(batch_job.results):
    print(f"\n[{idx + 1}] {result.job_posting.company_name} - {result.job_posting.job_title}")
    print("-" * 70)

    if result.hr_contact:
        print(f"Contact: {result.hr_contact.name} - {result.hr_contact.role}")
        print(f"LinkedIn: {result.hr_contact.profile_url}")
        print(f"Confidence: {result.hr_contact.confidence_score}")
    else:
        print("Contact: None found")
        if result.error_message:
            print(f"Error: {result.error_message}")

    print(f"\nReasoning: {result.reasoning[:200]}...")

    if result.outreach_message:
        print(f"\n✅ OUTREACH MESSAGE ({len(result.outreach_message)} chars):")
        print("-" * 70)
        print(result.outreach_message)
    else:
        print("\n❌ NO OUTREACH MESSAGE GENERATED")
        print("   Possible reasons:")
        print("   - CV profile not passed correctly")
        print("   - Message generator failed")
        print("   - Contact not found (messages only generated if contact found)")

print("\n" + "=" * 70)
print("✅ Test Complete!")
print("=" * 70)
