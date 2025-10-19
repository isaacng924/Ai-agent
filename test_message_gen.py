"""Test message generation flow."""

import logging
logging.basicConfig(level=logging.INFO)

from src.services.cv_parser import CVParser
from src.services.message_generator import MessageGenerator
from src.models.job_posting import JobPosting
from src.models.hr_contact import HRContact, ContactSource

print("=" * 60)
print("Testing Message Generation Flow")
print("=" * 60)

# Step 1: Parse CV
print("\n1. Parsing CV...")
parser = CVParser()
cv_profile = parser.parse_file("test_cv_simple.txt")
print(f"✓ CV Parsed: {cv_profile.full_name}")
print(f"  Skills: {', '.join(cv_profile.skills[:5])}")

# Step 2: Create mock job and contact
print("\n2. Creating mock job posting and HR contact...")
job_posting = JobPosting(
    company_name="Google",
    job_title="Senior Software Engineer",
    description="We're looking for an experienced engineer to join our cloud infrastructure team."
)
print(f"✓ Job: {job_posting.company_name} - {job_posting.job_title}")

hr_contact = HRContact(
    name="Jane Smith",
    role="Technical Recruiter",
    company="Google",
    profile_url="https://linkedin.com/in/janesmith",
    source=ContactSource.WEB_SEARCH,
    confidence_score=0.9,
)
print(f"✓ Contact: {hr_contact.name} - {hr_contact.role}")

# Step 3: Generate message
print("\n3. Generating personalized message...")
print("   (This will call AWS Bedrock - may take 10-15 seconds)")

try:
    generator = MessageGenerator()
    print("   ✓ MessageGenerator initialized")

    message = generator.generate_message(
        cv_profile=cv_profile,
        job_posting=job_posting,
        hr_contact=hr_contact,
        tone="professional",
        channel="linkedin",
        length="medium",
    )

    print("\n" + "=" * 60)
    print("✅ Message Generated Successfully!")
    print("=" * 60)
    print(message)
    print("=" * 60)
    print(f"\nMessage length: {len(message)} characters")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
