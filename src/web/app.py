"""Streamlit web UI for AI Job Connector Agent."""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
from io import BytesIO
from datetime import datetime

from src.models.job_posting import JobPosting
from src.models.batch_job import BatchJob
from src.models.cv_profile import CVProfile
from src.services.cv_parser import CVParser
from src.agent.runtime import AgentRuntime
from src.agent.orchestrator import process_batch_job
from src.utils.config import get_config


# File upload limits (in bytes)
MAX_CV_SIZE = 5 * 1024 * 1024  # 5 MB for CV/PDF files
MAX_JSON_SIZE = 1 * 1024 * 1024  # 1 MB for JSON batch files


# Page configuration
st.set_page_config(
    page_title="AI Job Connector",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_session_state():
    """Initialize session state variables."""
    if "cv_profile" not in st.session_state:
        st.session_state.cv_profile = None
    if "job_postings" not in st.session_state:
        st.session_state.job_postings = []
    if "batch_results" not in st.session_state:
        st.session_state.batch_results = None
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "last_uploaded_json_name" not in st.session_state:
        st.session_state.last_uploaded_json_name = None


def render_header():
    """Render page header."""
    st.title("🤖 AI Job Connector Agent")
    st.markdown(
        """
        **Find HR contacts and generate personalized outreach messages automatically**

        Upload your CV and job listings to get HR contact information with
        ready-to-send LinkedIn/email messages powered by AWS Bedrock.
        """
    )
    st.divider()


def render_sidebar():
    """Render sidebar with configuration options."""
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Check configuration
        try:
            config = get_config()
            st.success("✓ AWS Bedrock configured")
            st.caption(f"Model: {config.bedrock_model_id}")
            st.caption(f"Region: {config.aws_region}")
        except Exception as e:
            st.error("❌ AWS configuration error")
            st.caption(str(e))
            return False

        st.divider()

        # Message settings
        st.subheader("Message Settings")

        tone = st.selectbox(
            "Tone",
            ["professional", "friendly", "formal", "enthusiastic"],
            index=0,
            help="The tone of the generated messages",
        )

        channel = st.selectbox(
            "Channel",
            ["linkedin", "email", "generic"],
            index=0,
            help="Target channel for the messages",
        )

        length = st.selectbox(
            "Length",
            ["short", "medium", "long"],
            index=1,
            help="Desired message length",
        )

        st.session_state.message_tone = tone
        st.session_state.message_channel = channel
        st.session_state.message_length = length

        st.divider()

        # About
        st.subheader("About")
        st.caption(
            "Built with AWS Bedrock & Claude 3.5 Sonnet\n\n"
            "Part of AWS AI Agent Hackathon 2025"
        )

        return True


def render_cv_upload():
    """Render CV upload section."""
    st.header("1️⃣ Upload Your CV/Resume")

    uploaded_file = st.file_uploader(
        "Choose your CV file",
        type=["pdf", "txt", "docx"],
        help=f"Upload your resume in PDF, TXT, or DOCX format (max {MAX_CV_SIZE // (1024*1024)} MB)",
    )

    if uploaded_file:
        # Check file size
        file_size = uploaded_file.size
        if file_size > MAX_CV_SIZE:
            st.error(
                f"❌ File too large: {file_size / (1024*1024):.2f} MB. "
                f"Maximum allowed size is {MAX_CV_SIZE // (1024*1024)} MB."
            )
            return

        with st.spinner("Parsing your CV..."):
            try:
                # Read file bytes
                file_bytes = uploaded_file.read()
                file_extension = Path(uploaded_file.name).suffix.lower()

                # Parse CV
                parser = CVParser()
                cv_profile = parser.parse_bytes(file_bytes, file_extension)

                st.session_state.cv_profile = cv_profile

                # Display parsed information
                st.success("✓ CV parsed successfully!")

                with st.expander("View Parsed CV Information"):
                    if cv_profile.full_name:
                        st.write(f"**Name:** {cv_profile.full_name}")
                    if cv_profile.email:
                        st.write(f"**Email:** {cv_profile.email}")
                    if cv_profile.summary:
                        st.write(f"**Summary:** {cv_profile.summary}")
                    if cv_profile.skills:
                        st.write(f"**Skills:** {', '.join(cv_profile.skills[:10])}")
                    if cv_profile.experience:
                        st.write("**Experience:**")
                        for exp in cv_profile.experience[:3]:
                            st.write(f"- {exp}")
                    if cv_profile.education:
                        st.write("**Education:**")
                        for edu in cv_profile.education[:2]:
                            st.write(f"- {edu}")

            except Exception as e:
                st.error(f"Failed to parse CV: {str(e)}")
                st.session_state.cv_profile = None

    elif st.session_state.cv_profile:
        st.info(f"✓ CV loaded: {st.session_state.cv_profile.full_name or 'Unnamed'}")


def render_job_input():
    """Render job listings input section."""
    st.header("2️⃣ Add Job Listings")

    # Tab for manual vs batch input
    tab1, tab2 = st.tabs(["Manual Input", "Upload JSON"])

    with tab1:
        st.subheader("Add Jobs Manually")

        col1, col2 = st.columns(2)

        with col1:
            company = st.text_input("Company Name", placeholder="e.g., Google")
            title = st.text_input("Job Title", placeholder="e.g., Software Engineer")

        with col2:
            url = st.text_input("Job URL (optional)", placeholder="https://...")
            description = st.text_area(
                "Job Description (optional)",
                placeholder="Key requirements and responsibilities...",
                height=100,
            )

        if st.button("➕ Add Job", type="primary"):
            if company and title:
                job = JobPosting(
                    company_name=company,
                    job_title=title,
                    job_url=url if url else None,
                    description=description if description else None,
                )
                st.session_state.job_postings.append(job)
                st.success(f"Added: {company} - {title}")
                st.rerun()
            else:
                st.error("Please enter company name and job title")

    with tab2:
        st.subheader("Upload Batch JSON")
        st.caption(
            f"Upload a JSON file with job listings (max {MAX_JSON_SIZE // (1024*1024)} MB). "
            "Format: `[{\"company_name\": \"...\", \"job_title\": \"...\"}]`"
        )

        uploaded_json = st.file_uploader(
            "Choose JSON file",
            type=["json"],
            key="json_uploader",
        )

        if uploaded_json:
            # Check file size
            file_size = uploaded_json.size
            if file_size > MAX_JSON_SIZE:
                st.error(
                    f"❌ File too large: {file_size / (1024*1024):.2f} MB. "
                    f"Maximum allowed size is {MAX_JSON_SIZE // (1024*1024)} MB."
                )
            else:
                # Check if this file was already processed
                if "last_uploaded_json_name" not in st.session_state:
                    st.session_state.last_uploaded_json_name = None

                if st.session_state.last_uploaded_json_name != uploaded_json.name:
                    try:
                        job_data = json.load(uploaded_json)
                        jobs = [JobPosting(**job) for job in job_data]
                        st.session_state.job_postings.extend(jobs)
                        st.session_state.last_uploaded_json_name = uploaded_json.name
                        st.success(f"✓ Loaded {len(jobs)} jobs from JSON")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to load JSON: {str(e)}")
                        st.exception(e)
                else:
                    st.info(f"✓ File '{uploaded_json.name}' already loaded")

    # Display current jobs
    if st.session_state.job_postings:
        st.divider()
        st.subheader(f"Current Jobs ({len(st.session_state.job_postings)})")

        # Create dataframe for display
        jobs_df = pd.DataFrame([
            {
                "Company": job.company_name,
                "Job Title": job.job_title,
                "Has URL": "✓" if job.job_url else "",
                "Has Description": "✓" if job.description else "",
            }
            for job in st.session_state.job_postings
        ])

        st.dataframe(jobs_df, use_container_width=True, hide_index=True)

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ Clear All Jobs"):
                st.session_state.job_postings = []
                st.rerun()


def render_process_section():
    """Render processing section."""
    st.header("3️⃣ Process & Generate Messages")

    # Check if ready to process
    if not st.session_state.cv_profile:
        st.warning("⚠️ Please upload your CV first")
        return

    if not st.session_state.job_postings:
        st.warning("⚠️ Please add at least one job listing")
        return

    # Ready to process
    st.success(
        f"✓ Ready to process {len(st.session_state.job_postings)} jobs "
        f"with CV: {st.session_state.cv_profile.full_name or 'Unnamed'}"
    )

    if st.button("🚀 Start Processing", type="primary", disabled=st.session_state.processing):
        process_jobs()


def process_jobs():
    """Process all jobs and generate messages."""
    st.session_state.processing = True

    # Create batch job
    batch_job = BatchJob(job_postings=st.session_state.job_postings)

    # Initialize runtime
    agent_runtime = AgentRuntime()

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()

    def progress_callback(current, total, result):
        """Update progress UI."""
        progress = current / total
        progress_bar.progress(progress)
        status_text.text(
            f"Processing {current}/{total}: {result.job_posting.company_name} - "
            f"{'Found: ' + result.hr_contact.name if result.hr_contact else 'No contact'}"
        )

    # Process batch
    try:
        with st.spinner("Finding HR contacts and generating messages..."):
            batch_job = process_batch_job(
                batch_job=batch_job,
                agent_runtime=agent_runtime,
                progress_callback=progress_callback,
                cv_profile=st.session_state.cv_profile,
                message_tone=st.session_state.get("message_tone", "professional"),
                message_channel=st.session_state.get("message_channel", "linkedin"),
                message_length=st.session_state.get("message_length", "medium"),
            )

        st.session_state.batch_results = batch_job
        progress_bar.progress(1.0)
        status_text.text("✓ Processing complete!")

        # Debug: Check message generation
        messages_count = sum(1 for r in batch_job.results if r.outreach_message)
        print(f"DEBUG: Processing complete. Messages generated: {messages_count}/{len(batch_job.results)}")
        for idx, result in enumerate(batch_job.results):
            has_contact = result.hr_contact is not None
            has_message = result.outreach_message is not None
            msg_len = len(result.outreach_message) if result.outreach_message else 0
            print(f"  Result {idx}: contact={has_contact}, message={has_message}, length={msg_len}")

        st.success(
            f"✓ Completed! Found {len(batch_job.results) - batch_job.error_count} "
            f"out of {len(batch_job.job_postings)} contacts"
        )

        st.rerun()

    except Exception as e:
        st.error(f"Processing failed: {str(e)}")

    finally:
        st.session_state.processing = False


def render_results():
    """Render results section."""
    st.header("4️⃣ Results & Download")

    batch_job = st.session_state.batch_results

    if not batch_job:
        st.info("No results yet. Process jobs to see results here.")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Jobs", len(batch_job.job_postings))
    with col2:
        st.metric("Contacts Found", len(batch_job.results) - batch_job.error_count)
    with col3:
        messages_count = sum(1 for r in batch_job.results if r.outreach_message)
        st.metric("Messages Generated", messages_count)
    with col4:
        st.metric("Status", batch_job.status.value.title())

    st.divider()

    # Results table with expandable messages
    for idx, result in enumerate(batch_job.results):
        with st.expander(
            f"{idx + 1}. {result.job_posting.company_name} - {result.job_posting.job_title} "
            f"{'✓' if result.hr_contact else '✗'}",
            expanded=False,
        ):
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("Job Details")
                st.write(f"**Company:** {result.job_posting.company_name}")
                st.write(f"**Title:** {result.job_posting.job_title}")
                if result.job_posting.job_url:
                    st.write(f"**URL:** {result.job_posting.job_url}")

            with col2:
                st.subheader("HR Contact")
                if result.hr_contact:
                    st.write(f"**Name:** {result.hr_contact.name}")
                    st.write(f"**Role:** {result.hr_contact.role}")
                    if result.hr_contact.profile_url:
                        st.write(f"**LinkedIn:** {result.hr_contact.profile_url}")
                    st.write(f"**Confidence:** {result.hr_contact.confidence_score:.2f}")
                else:
                    st.warning("No contact found")
                    if result.error_message:
                        st.error(result.error_message)

            if result.reasoning:
                st.subheader("Reasoning")
                st.write(result.reasoning[:300] + "..." if len(result.reasoning) > 300 else result.reasoning)

            if result.outreach_message:
                st.subheader("Outreach Message")
                st.text_area(
                    "Generated message (ready to copy)",
                    value=result.outreach_message,
                    height=200,
                    key=f"message_{idx}",
                )

                # Copy button (uses clipboard API)
                st.caption("💡 Click in the box and press Ctrl+A (Cmd+A) then Ctrl+C (Cmd+C) to copy")

    st.divider()

    # Download section
    st.subheader("📥 Download Results")

    col1, col2 = st.columns(2)

    with col1:
        # Generate CSV
        csv_data = generate_csv(batch_job)
        st.download_button(
            label="Download CSV (with messages)",
            data=csv_data,
            file_name=f"job_connector_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col2:
        # Generate JSON
        json_data = generate_json(batch_job)
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name=f"job_connector_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )


def generate_csv(batch_job: BatchJob) -> str:
    """Generate CSV file content."""
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Company",
        "Job Title",
        "Contact Found",
        "Contact Name",
        "Contact Role",
        "LinkedIn URL",
        "Confidence Score",
        "Outreach Message",
        "Status",
    ])

    # Data rows
    for result in batch_job.results:
        writer.writerow([
            result.job_posting.company_name,
            result.job_posting.job_title,
            "Yes" if result.hr_contact else "No",
            result.hr_contact.name if result.hr_contact else "",
            result.hr_contact.role if result.hr_contact else "",
            str(result.hr_contact.profile_url) if result.hr_contact and result.hr_contact.profile_url else "",
            f"{result.hr_contact.confidence_score:.2f}" if result.hr_contact else "",
            result.outreach_message or "",
            "Success" if result.hr_contact else ("Error" if result.error_message else "No Contact"),
        ])

    return output.getvalue()


def generate_json(batch_job: BatchJob) -> str:
    """Generate JSON file content."""
    data = {
        "batch_id": batch_job.id,
        "status": batch_job.status.value,
        "total_jobs": len(batch_job.job_postings),
        "successful": len(batch_job.results) - batch_job.error_count,
        "created_at": batch_job.created_at.isoformat(),
        "results": [
            {
                "company": result.job_posting.company_name,
                "job_title": result.job_posting.job_title,
                "hr_contact": {
                    "name": result.hr_contact.name if result.hr_contact else None,
                    "role": result.hr_contact.role if result.hr_contact else None,
                    "profile_url": str(result.hr_contact.profile_url) if result.hr_contact and result.hr_contact.profile_url else None,
                    "confidence": result.hr_contact.confidence_score if result.hr_contact else None,
                } if result.hr_contact else None,
                "outreach_message": result.outreach_message,
                "reasoning": result.reasoning,
                "error": result.error_message,
            }
            for result in batch_job.results
        ],
    }

    return json.dumps(data, indent=2)


def main():
    """Main application entry point."""
    initialize_session_state()

    # Render sidebar and check config
    config_ok = render_sidebar()

    if not config_ok:
        st.error("Please configure AWS Bedrock before using the application.")
        st.info("Check your .env file and ensure AWS credentials are set up correctly.")
        return

    # Render main sections
    render_header()
    render_cv_upload()
    st.divider()
    render_job_input()
    st.divider()
    render_process_section()
    st.divider()
    render_results()


if __name__ == "__main__":
    main()
