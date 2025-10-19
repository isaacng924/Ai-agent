"""Main CLI entry point for Job Connector Agent."""

import click
import json
import csv
import logging
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.models.job_posting import JobPosting
from src.models.batch_job import BatchJob
from src.agent.runtime import AgentRuntime
from src.agent.orchestrator import process_batch_job, process_single_job
from src.utils.config import get_config

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
    AI Job Connector Agent CLI.

    Discover HR contacts and generate outreach messages for job applications.
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
    Search for HR contacts for a single job posting.

    Example:
        job-connector search -c "Anthropic" -t "AI Researcher"
    """
    console.print(
        Panel.fit(
            f"[bold blue]Job Connector Agent[/bold blue]\n"
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

    # Initialize agent runtime
    try:
        config = get_config()
        console.print(f"\nUsing model: [cyan]{config.bedrock_model_id}[/cyan]")
    except ValueError as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        console.print(
            "\n[yellow]Tip: Make sure you have set up your .env file with required variables.[/yellow]"
        )
        return

    agent_runtime = AgentRuntime()

    # Process search with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Searching for HR contacts...", total=None)

        try:
            result = process_single_job(job_posting, agent_runtime)
            progress.update(task, completed=True)

        except Exception as e:
            progress.stop()
            console.print(f"\n[red]Error during search: {str(e)}[/red]")
            return

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
    help="Output file for batch results (JSON or CSV, determined by extension)",
)
@click.option(
    "--format",
    type=click.Choice(["json", "csv", "both"], case_sensitive=False),
    default="json",
    help="Output format: json, csv, or both",
)
def batch(file: str, output: Optional[str], format: str):
    """
    Process multiple job postings from a JSON file.

    Example:
        job-connector batch -f jobs.json -o results.json

    JSON file format:
    [
        {"company_name": "Anthropic", "job_title": "AI Researcher"},
        {"company_name": "OpenAI", "job_title": "Software Engineer"}
    ]
    """
    console.print(
        Panel.fit(
            f"[bold blue]Job Connector Agent[/bold blue]\n" f"Processing batch from {file}",
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

    # Initialize agent runtime
    try:
        config = get_config()
        console.print(f"Using model: [cyan]{config.bedrock_model_id}[/cyan]\n")
    except ValueError as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        return

    agent_runtime = AgentRuntime()

    # Process batch with real-time progress tracking
    with Progress(console=console) as progress:
        task = progress.add_task(
            "[cyan]Processing job postings...", total=len(job_postings)
        )

        def update_progress(current, total, result):
            """Progress callback to update UI in real-time."""
            progress.update(task, completed=current)
            console.print(
                f"[dim]✓ {result.job_posting.company_name} - "
                f"{'Found: ' + result.hr_contact.name if result.hr_contact else 'No contact'}[/dim]"
            )

        try:
            batch_job = process_batch_job(batch_job, agent_runtime, progress_callback=update_progress)

        except Exception as e:
            console.print(f"\n[red]Error during batch processing: {str(e)}[/red]")
            return

    # Display summary
    _display_batch_summary(batch_job)

    # Save results if requested
    if output:
        output_path = Path(output)

        # Determine format from extension or flag
        if format == "both":
            # Save both formats
            json_path = output_path.with_suffix('.json')
            csv_path = output_path.with_suffix('.csv')
            _save_batch_to_file(batch_job, str(json_path))
            _save_batch_to_csv(batch_job, str(csv_path))
            console.print(f"\n[green]Results saved to:[/green]")
            console.print(f"  - JSON: {json_path}")
            console.print(f"  - CSV: {csv_path}")
        elif format == "csv" or output_path.suffix.lower() == '.csv':
            _save_batch_to_csv(batch_job, output)
            console.print(f"\n[green]Batch results saved to {output} (CSV)[/green]")
        else:
            _save_batch_to_file(batch_job, output)
            console.print(f"\n[green]Batch results saved to {output} (JSON)[/green]")


@cli.command()
def demo():
    """
    Run a demo with sample job postings.

    Uses the test fixtures to demonstrate the agent's capabilities.
    """
    console.print(
        Panel.fit(
            "[bold blue]Job Connector Agent Demo[/bold blue]\n"
            "Processing sample job postings from fixtures",
            title="Demo Mode",
        )
    )

    # Load fixture data
    fixture_path = Path(__file__).parent.parent.parent / "tests/fixtures/mock_job_postings.json"

    if not fixture_path.exists():
        console.print(
            f"[red]Fixture file not found: {fixture_path}[/red]"
        )
        return

    try:
        with open(fixture_path, "r") as f:
            job_data = json.load(f)

        # Use first 3 jobs for demo
        job_postings = [JobPosting(**job) for job in job_data[:3]]
        console.print(f"\n[green]Running demo with {len(job_postings)} sample jobs[/green]\n")

    except Exception as e:
        console.print(f"[red]Error loading fixtures: {str(e)}[/red]")
        return

    # Create batch job
    batch_job = BatchJob(job_postings=job_postings)

    # Initialize agent runtime
    try:
        config = get_config()
        console.print(f"Using model: [cyan]{config.bedrock_model_id}[/cyan]\n")
    except ValueError as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        console.print(
            "\n[yellow]Tip: Run 'make install' and set up your .env file first.[/yellow]"
        )
        return

    agent_runtime = AgentRuntime()

    # Process batch
    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Processing demo jobs...", total=len(job_postings))

        try:
            batch_job = process_batch_job(batch_job, agent_runtime)

            for i in range(len(job_postings)):
                progress.update(task, advance=1)

        except Exception as e:
            console.print(f"\n[red]Error during demo: {str(e)}[/red]")
            return

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
    else:
        console.print(f"\n[bold yellow]⚠ No contact found[/bold yellow]")

        if result.suggestions:
            console.print(f"\n[bold]Suggestions:[/bold]")
            for suggestion in result.suggestions:
                console.print(f"  • {suggestion}")

    console.print(f"\n[bold]Reasoning:[/bold]")
    console.print(f"  {result.reasoning}")

    console.print(f"\n[dim]Search duration: {result.search_duration_seconds:.2f}s[/dim]")

    if result.error_message:
        console.print(f"\n[red]Error: {result.error_message}[/red]")


def _display_batch_summary(batch_job: BatchJob):
    """Display batch job summary with rich table."""
    console.print(f"\n[bold]Batch Job Summary:[/bold]")
    console.print(f"  Status: {batch_job.status.value}")
    console.print(f"  Total jobs: {len(batch_job.job_postings)}")
    console.print(f"  Successful: {len(batch_job.results) - batch_job.error_count}")
    console.print(f"  Failed: {batch_job.error_count}")

    # Create results table
    table = Table(title="\nResults Overview", show_header=True, header_style="bold cyan")
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


def _save_batch_to_file(batch_job: BatchJob, filepath: str):
    """Save batch job results to JSON file."""
    output_data = {
        "batch_id": batch_job.id,
        "status": batch_job.status.value,
        "total_jobs": len(batch_job.job_postings),
        "successful": len(batch_job.results) - batch_job.error_count,
        "failed": batch_job.error_count,
        "created_at": batch_job.created_at.isoformat(),
        "completed_at": batch_job.completed_at.isoformat() if batch_job.completed_at else None,
        "results": [
            {
                "job_posting": result.job_posting.model_dump(mode='json'),
                "hr_contact": result.hr_contact.model_dump(mode='json') if result.hr_contact else None,
                "reasoning": result.reasoning,
                "search_duration_seconds": result.search_duration_seconds,
                "error_message": result.error_message,
            }
            for result in batch_job.results
        ],
    }

    with open(filepath, "w") as f:
        json.dump(output_data, f, indent=2)


def _save_batch_to_csv(batch_job: BatchJob, filepath: str):
    """Save batch job results to CSV file."""
    with open(filepath, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow([
            "Company",
            "Job Title",
            "Contact Found",
            "Contact Name",
            "Contact Role",
            "LinkedIn URL",
            "Confidence Score",
            "Source",
            "Search Duration (s)",
            "Reasoning",
            "Status",
            "Error Message"
        ])

        # Write data rows
        for result in batch_job.results:
            contact_found = "Yes" if result.hr_contact else "No"
            contact_name = result.hr_contact.name if result.hr_contact else ""
            contact_role = result.hr_contact.role if result.hr_contact else ""
            profile_url = str(result.hr_contact.profile_url) if result.hr_contact and result.hr_contact.profile_url else ""
            confidence = f"{result.hr_contact.confidence_score:.2f}" if result.hr_contact else ""
            source = result.hr_contact.source.value if result.hr_contact else ""
            status = "Success" if result.hr_contact else ("Error" if result.error_message else "No Contact Found")

            writer.writerow([
                result.job_posting.company_name,
                result.job_posting.job_title,
                contact_found,
                contact_name,
                contact_role,
                profile_url,
                confidence,
                source,
                f"{result.search_duration_seconds:.2f}",
                result.reasoning[:200] + "..." if len(result.reasoning) > 200 else result.reasoning,
                status,
                result.error_message or ""
            ])

        # Write summary row
        writer.writerow([])  # Empty row
        writer.writerow([
            "SUMMARY",
            f"Total: {len(batch_job.job_postings)}",
            f"Successful: {len(batch_job.results) - batch_job.error_count}",
            f"Failed: {batch_job.error_count}",
            f"Status: {batch_job.status.value}",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
        ])


if __name__ == "__main__":
    cli()
