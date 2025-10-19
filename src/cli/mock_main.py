"""CLI with mock mode support (no real APIs required)."""

import click
import json
import logging
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.models.job_posting import JobPosting
from src.models.batch_job import BatchJob
from src.agent.mock_runtime import MockAgentRuntime
from src.agent.orchestrator import process_batch_job

console = Console()


def setup_logging(verbose: bool = False):
    """Configure logging for CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose: bool):
    """
    AI Job Connector Agent CLI (Mock Mode).

    Test the full functionality without real API keys.
    """
    setup_logging(verbose)


@cli.command()
@click.option(
    "--company",
    "-c",
    required=True,
    help="Company name (e.g., 'Anthropic', 'Amazon')",
)
@click.option(
    "--title",
    "-t",
    required=True,
    help="Job title (e.g., 'Software Engineer', 'Data Scientist')",
)
@click.option(
    "--description",
    "-d",
    help="Optional job description for better context",
)
@click.option(
    "--url",
    "-u",
    help="Optional URL to the job posting",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file for results (JSON)",
)
def search(
    company: str,
    title: str,
    description: Optional[str],
    url: Optional[str],
    output: Optional[str],
):
    """
    Search for HR contacts for a single job posting (MOCK MODE).

    Example:
        job-connector-mock search -c "Anthropic" -t "AI Researcher"
    """
    console.print(
        Panel.fit(
            f"[bold blue]Job Connector Agent (Mock Mode)[/bold blue]\n"
            f"Searching for HR contacts at {company} for {title}",
            title="Search",
        )
    )

    # Create job posting
    job_posting = JobPosting(
        company_name=company,
        job_title=title,
        description=description,
        job_url=url,
    )

    # Use mock agent runtime
    agent_runtime = MockAgentRuntime()

    # Process search with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Searching for HR contacts (mock)...", total=None)

        result = agent_runtime.discover_contact(job_posting)
        progress.update(task, completed=True)

    # Display results
    _display_search_result(result)

    # Save to file if requested
    if output:
        _save_result_to_file(result, output)
        console.print(f"\n[green]Results saved to {output}[/green]")


@cli.command()
@click.option(
    "--file",
    "-f",
    required=True,
    type=click.Path(exists=True),
    help="JSON file with list of job postings",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file for batch results (JSON)",
)
def batch(file: str, output: Optional[str]):
    """
    Process multiple job postings from a JSON file (MOCK MODE).

    Example:
        job-connector-mock batch -f jobs.json -o results.json

    JSON file format:
    [
        {"company_name": "Anthropic", "job_title": "AI Researcher"},
        {"company_name": "OpenAI", "job_title": "Software Engineer"}
    ]
    """
    console.print(
        Panel.fit(
            f"[bold blue]Job Connector Agent (Mock Mode)[/bold blue]\n"
            f"Processing batch from {file}",
            title="Batch Processing",
        )
    )

    # Load job postings from file
    try:
        with open(file, "r") as f:
            job_data = json.load(f)

        job_postings = [JobPosting(**job) for job in job_data]
        console.print(f"\n[green]Loaded {len(job_postings)} job postings[/green]")

    except Exception as e:
        console.print(f"[red]Error loading file: {str(e)}[/red]")
        return

    # Create batch job
    batch_job = BatchJob(job_postings=job_postings)

    # Use mock agent runtime
    agent_runtime = MockAgentRuntime()

    console.print(f"[cyan]Using mock agent runtime (no real APIs)[/cyan]\n")

    # Process batch with progress indicator
    with Progress(console=console) as progress:
        task = progress.add_task(
            "[cyan]Processing job postings (mock)...", total=len(job_postings)
        )

        # Process batch
        batch_job = process_batch_job(batch_job, agent_runtime)

        # Update progress
        progress.update(task, completed=len(job_postings))

    # Display summary
    _display_batch_summary(batch_job)

    # Save results if requested
    if output:
        _save_batch_to_file(batch_job, output)
        console.print(f"\n[green]Batch results saved to {output}[/green]")


@cli.command()
def demo():
    """
    Run a demo with sample job postings (MOCK MODE).

    Uses test fixtures to demonstrate the agent's capabilities.
    """
    console.print(
        Panel.fit(
            "[bold blue]Job Connector Agent Demo (Mock Mode)[/bold blue]\n"
            "Processing sample job postings with mock data",
            title="Demo Mode",
        )
    )

    # Load fixture data
    fixture_path = (
        Path(__file__).parent.parent.parent
        / "tests/fixtures/mock_job_postings.json"
    )

    if not fixture_path.exists():
        console.print(f"[red]Fixture file not found: {fixture_path}[/red]")
        return

    try:
        with open(fixture_path, "r") as f:
            job_data = json.load(f)

        # Use first 3 jobs for demo
        job_postings = [JobPosting(**job) for job in job_data[:3]]
        console.print(
            f"\n[green]Running demo with {len(job_postings)} sample jobs[/green]\n"
        )

    except Exception as e:
        console.print(f"[red]Error loading fixtures: {str(e)}[/red]")
        return

    # Create batch job
    batch_job = BatchJob(job_postings=job_postings)

    # Use mock agent runtime
    agent_runtime = MockAgentRuntime()
    console.print(f"[cyan]Using mock agent runtime (no real APIs required)[/cyan]\n")

    # Process batch
    with Progress(console=console) as progress:
        task = progress.add_task(
            "[cyan]Processing demo jobs...", total=len(job_postings)
        )

        batch_job = process_batch_job(batch_job, agent_runtime)

        for i in range(len(job_postings)):
            progress.update(task, advance=1)

    # Display results
    _display_batch_summary(batch_job)

    # Show detailed results for first job
    if batch_job.results:
        console.print("\n[bold]Detailed result for first job:[/bold]")
        _display_search_result(batch_job.results[0])


def _display_search_result(result):
    """Display a single search result with rich formatting."""
    console.print(f"\n[bold]Job Posting:[/bold]")
    console.print(f"  Company: {result.job_posting.company_name}")
    console.print(f"  Title: {result.job_posting.job_title}")

    if result.hr_contact:
        console.print(f"\n[bold green]✓ HR Contact Found:[/bold green]")
        console.print(f"  Name: {result.hr_contact.name}")
        console.print(f"  Role: {result.hr_contact.role}")
        console.print(f"  Source: {result.hr_contact.source.value}")
        console.print(f"  Confidence: {result.hr_contact.confidence_score:.2f}")

        if result.hr_contact.profile_url:
            console.print(f"  Profile: {result.hr_contact.profile_url}")

        if result.hr_contact.additional_info:
            if "note" in result.hr_contact.additional_info:
                console.print(
                    f"  [dim]{result.hr_contact.additional_info['note']}[/dim]"
                )
    else:
        console.print(f"\n[bold yellow]⚠ No contact found[/bold yellow]")

        if result.suggestions:
            console.print(f"\n[bold]Suggestions:[/bold]")
            for suggestion in result.suggestions:
                console.print(f"  • {suggestion}")

    console.print(f"\n[bold]Reasoning:[/bold]")
    console.print(f"  {result.reasoning}")

    console.print(
        f"\n[dim]Search duration: {result.search_duration_seconds:.2f}s[/dim]"
    )

    if result.error_message:
        console.print(f"\n[red]Error: {result.error_message}[/red]")


def _display_batch_summary(batch_job):
    """Display batch job summary with rich table."""
    console.print(f"\n[bold]Batch Job Summary:[/bold]")
    console.print(f"  Status: {batch_job.status.value}")
    console.print(f"  Total jobs: {len(batch_job.job_postings)}")
    console.print(f"  Successful: {len(batch_job.results) - batch_job.error_count}")
    console.print(f"  Failed: {batch_job.error_count}")

    # Create results table
    table = Table(
        title="\nResults Overview", show_header=True, header_style="bold cyan"
    )
    table.add_column("Company", style="cyan")
    table.add_column("Job Title", style="magenta")
    table.add_column("Contact Found", style="green")
    table.add_column("Confidence", justify="right")

    for result in batch_job.results:
        contact_status = "✓" if result.hr_contact else "✗"
        confidence = (
            f"{result.hr_contact.confidence_score:.2f}"
            if result.hr_contact
            else "N/A"
        )

        table.add_row(
            result.job_posting.company_name,
            result.job_posting.job_title[:40],
            contact_status,
            confidence,
        )

    console.print(table)


def _save_result_to_file(result, filepath: str):
    """Save search result to JSON file."""
    output_data = {
        "job_posting": result.job_posting.model_dump(),
        "hr_contact": result.hr_contact.model_dump() if result.hr_contact else None,
        "reasoning": result.reasoning,
        "search_duration_seconds": result.search_duration_seconds,
        "timestamp": result.timestamp.isoformat(),
        "error_message": result.error_message,
        "suggestions": result.suggestions,
    }

    with open(filepath, "w") as f:
        json.dump(output_data, f, indent=2)


def _save_batch_to_file(batch_job, filepath: str):
    """Save batch job results to JSON file."""
    output_data = {
        "batch_id": batch_job.id,
        "status": batch_job.status.value,
        "total_jobs": len(batch_job.job_postings),
        "successful": len(batch_job.results) - batch_job.error_count,
        "failed": batch_job.error_count,
        "created_at": batch_job.created_at.isoformat(),
        "completed_at": (
            batch_job.completed_at.isoformat() if batch_job.completed_at else None
        ),
        "results": [
            {
                "job_posting": result.job_posting.model_dump(),
                "hr_contact": (
                    result.hr_contact.model_dump() if result.hr_contact else None
                ),
                "reasoning": result.reasoning,
                "search_duration_seconds": result.search_duration_seconds,
                "error_message": result.error_message,
            }
            for result in batch_job.results
        ],
    }

    with open(filepath, "w") as f:
        json.dump(output_data, f, indent=2)


if __name__ == "__main__":
    cli()
