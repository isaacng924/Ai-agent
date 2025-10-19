"""Quick test of CV parser functionality."""

from src.services.cv_parser import CVParser

# Test with simple text file
parser = CVParser()

print("Testing CV Parser...")
print("=" * 60)

cv_profile = parser.parse_file("test_cv_simple.txt")

print(f"✓ CV Parsed Successfully\n")
print(f"Name: {cv_profile.full_name}")
print(f"Email: {cv_profile.email}")
print(f"Phone: {cv_profile.phone}")
print(f"\nSummary:\n{cv_profile.summary}\n")
print(f"Skills ({len(cv_profile.skills)}): {', '.join(cv_profile.skills)}\n")
print(f"Experience ({len(cv_profile.experience)}):")
for exp in cv_profile.experience:
    print(f"  - {exp[:80]}{'...' if len(exp) > 80 else ''}")
print(f"\nEducation ({len(cv_profile.education)}):")
for edu in cv_profile.education:
    print(f"  - {edu}")

print("\n" + "=" * 60)
print("Summary for message generation:")
print("=" * 60)
print(cv_profile.to_summary_text())
print("\n✅ Test completed successfully!")
