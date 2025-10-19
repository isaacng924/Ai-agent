#!/usr/bin/env python3
"""
Test script for mock version (no real APIs required).

This script demonstrates full functionality using mock data.
"""

import json
from src.models.job_posting import JobPosting
from src.models.batch_job import BatchJob
from src.agent.mock_runtime import MockAgentRuntime
from src.agent.orchestrator import process_batch_job
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def test_single_search():
    """Test single job search with mock runtime."""
    console.print(Panel.fit(
        "[bold blue]Test 1: Single Job Search[/bold blue]",
        title="Mock Test"
    ))

    # Create a job posting
    job = JobPosting(
        company_name="Anthropic",
        job_title="AI Safety Researcher",
        description="Research AI alignment and safety for large language models"
    )

    console.print(f"\n[cyan]Searching for:[/cyan]")
    console.print(f"  Company: {job.company_name}")
    console.print(f"  Title: {job.job_title}")

    # Use mock runtime
    runtime = MockAgentRuntime()
    result = runtime.discover_contact(job)

    # Display results
    console.print(f"\n[bold green]✓ Contact Found![/bold green]")
    console.print(f"  Name: {result.hr_contact.name}")
    console.print(f"  Role: {result.hr_contact.role}")
    console.print(f"  Source: {result.hr_contact.source.value}")
    console.print(f"  Confidence: {result.hr_contact.confidence_score:.2f}")
    if result.hr_contact.profile_url:
        console.print(f"  Profile: {result.hr_contact.profile_url}")

    console.print(f"\n[bold]Reasoning:[/bold]")
    console.print(f"  {result.reasoning}")

    console.print(f"\n[dim]Duration: {result.search_duration_seconds:.2f}s[/dim]")


def test_batch_processing():
    """Test batch processing with mock runtime."""
    console.print(Panel.fit(
        "[bold blue]Test 2: Batch Processing[/bold blue]",
        title="Mock Test"
    ))

    # Create multiple job postings
    jobs = [
        JobPosting(company_name="Anthropic", job_title="AI Safety Researcher"),
        JobPosting(company_name="OpenAI", job_title="Software Engineer"),
        JobPosting(company_name="Google DeepMind", job_title="Research Scientist"),
        JobPosting(company_name="Microsoft", job_title="AI Product Manager"),
        JobPosting(company_name="Meta", job_title="ML Infrastructure Engineer"),
    ]

    console.print(f"\n[cyan]Processing {len(jobs)} job postings...[/cyan]\n")

    # Create batch job
    batch = BatchJob(job_postings=jobs)

    # Process with mock runtime
    runtime = MockAgentRuntime()
    batch = process_batch_job(batch, runtime)

    # Display summary
    console.print(f"\n[bold]Batch Summary:[/bold]")
    console.print(f"  Status: {batch.status.value}")
    console.print(f"  Total: {len(batch.job_postings)}")
    console.print(f"  Successful: {len(batch.results) - batch.error_count}")
    console.print(f"  Failed: {batch.error_count}")

    # Create results table
    table = Table(title="\nResults", show_header=True, header_style="bold cyan")
    table.add_column("Company", style="cyan")
    table.add_column("Job Title", style="magenta")
    table.add_column("Contact", style="green")
    table.add_column("Role", style="yellow")
    table.add_column("Confidence", justify="right")

    for result in batch.results:
        contact_name = result.hr_contact.name if result.hr_contact else "N/A"
        contact_role = result.hr_contact.role if result.hr_contact else "N/A"
        confidence = (
            f"{result.hr_contact.confidence_score:.2f}"
            if result.hr_contact
            else "N/A"
        )

        table.add_row(
            result.job_posting.company_name,
            result.job_posting.job_title[:30],
            contact_name,
            contact_role[:30],
            confidence,
        )

    console.print(table)


def test_export_to_json():
    """Test exporting results to JSON."""
    console.print(Panel.fit(
        "[bold blue]Test 3: Export to JSON[/bold blue]",
        title="Mock Test"
    ))

    # Create and process a batch
    jobs = [
        JobPosting(company_name="Anthropic", job_title="AI Researcher"),
        JobPosting(company_name="Tesla", job_title="Autopilot Engineer"),
    ]

    batch = BatchJob(job_postings=jobs)
    runtime = MockAgentRuntime()
    batch = process_batch_job(batch, runtime)

    # Export to JSON
    output_data = {
        "batch_id": batch.id,
        "status": batch.status.value,
        "total_jobs": len(batch.job_postings),
        "successful": len(batch.results) - batch.error_count,
        "failed": batch.error_count,
        "results": [
            {
                "job_posting": {
                    "company_name": r.job_posting.company_name,
                    "job_title": r.job_posting.job_title,
                },
                "hr_contact": {
                    "name": r.hr_contact.name,
                    "role": r.hr_contact.role,
                    "company": r.hr_contact.company,
                    "profile_url": str(r.hr_contact.profile_url) if r.hr_contact.profile_url else None,
                    "source": r.hr_contact.source.value,
                    "confidence_score": r.hr_contact.confidence_score,
                } if r.hr_contact else None,
                "reasoning": r.reasoning,
                "duration_seconds": r.search_duration_seconds,
            }
            for r in batch.results
        ],
    }

    # Save to file
    output_file = "mock_test_results.json"
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    console.print(f"\n[green]✓ Results exported to {output_file}[/green]")
    console.print(f"\n[dim]Sample output:[/dim]")

    # Show first result
    if batch.results:
        first_result = batch.results[0]
        console.print(f"\nCompany: {first_result.job_posting.company_name}")
        console.print(f"Contact: {first_result.hr_contact.name if first_result.hr_contact else 'None'}")
        console.print(f"Reasoning: {first_result.reasoning[:100]}...")


def main():
    """Run all mock tests."""
    console.print(Panel.fit(
        "[bold green]🚀 AI Job Connector Agent - Mock Test Suite[/bold green]\n"
        "[dim]Testing without real APIs (using mock data)[/dim]",
        title="Welcome"
    ))

    try:
        # Test 1: Single search
        test_single_search()
        console.print("\n" + "="*60 + "\n")

        # Test 2: Batch processing
        test_batch_processing()
        console.print("\n" + "="*60 + "\n")

        # Test 3: Export to JSON
        test_export_to_json()

        console.print("\n" + "="*60 + "\n")
        console.print(Panel.fit(
            "[bold green]✅ All Mock Tests Passed![/bold green]\n\n"
            "[cyan]What this demonstrates:[/cyan]\n"
            "  • Single job search functionality\n"
            "  • Batch processing of multiple jobs\n"
            "  • JSON export capabilities\n"
            "  • Realistic contact discovery\n"
            "  • Reasoning generation\n\n"
            "[yellow]Next steps:[/yellow]\n"
            "  1. Configure real APIs (Tavily + AWS Bedrock)\n"
            "  2. Run: job-connector demo\n"
            "  3. Test with real job postings",
            title="Success!"
        ))

    except Exception as e:
        console.print(f"\n[red]✗ Error: {str(e)}[/red]")
        import traceback
        console.print(f"\n[dim]{traceback.format_exc()}[/dim]")


if __name__ == "__main__":
    main()
