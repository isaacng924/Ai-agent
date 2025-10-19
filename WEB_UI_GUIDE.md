# Web UI Guide - AI Job Connector Agent

## Overview

The AI Job Connector Agent now includes a user-friendly web interface built with Streamlit. This allows non-technical users to easily upload their CV, add job listings, and receive personalized outreach messages with HR contact information.

## Features

### 1. CV Upload & Parsing
- **Supported Formats**: PDF, TXT, DOCX
- **Automatic Extraction**: Name, email, phone, skills, experience, education
- **Visual Preview**: See parsed information before processing

### 2. Job Listing Input
- **Manual Entry**: Add jobs one by one through a form
- **Batch Upload**: Upload JSON file with multiple jobs
- **Live Preview**: See all jobs in a table before processing

### 3. Intelligent Processing
- **HR Contact Discovery**: Finds relevant recruiters for each job
- **Message Generation**: Creates personalized LinkedIn/email messages based on your CV
- **Real-time Progress**: Watch as each job is processed
- **Reasoning Display**: See why each contact was selected

### 4. Results & Export
- **Interactive Results**: Expandable cards for each job with full details
- **Copy-Paste Messages**: Ready-to-send outreach messages
- **CSV Export**: Download all results with contacts and messages for CRM import
- **JSON Export**: Get structured data for further processing

## Quick Start

### Installation

```bash
# Install dependencies
pip install streamlit PyPDF2 python-docx

# Or use make command
make install
```

### Launch Web UI

```bash
# Option 1: Using make
make web

# Option 2: Direct command
streamlit run src/web/app.py

# Option 3: Custom port
streamlit run src/web/app.py --server.port 8080
```

The web UI will open in your browser at `http://localhost:8501`

## User Guide

### Step 1: Upload Your CV

1. Click "Browse files" or drag-and-drop your CV
2. Supported formats: PDF, TXT, DOCX
3. Wait for parsing to complete
4. Review parsed information in the expandable section

**Tips:**
- Use a well-formatted CV for best results
- Include clear sections for Skills, Experience, and Education
- The parser looks for common keywords and patterns

### Step 2: Add Job Listings

**Option A: Manual Input**
1. Go to "Manual Input" tab
2. Enter company name and job title (required)
3. Optionally add job URL and description
4. Click "➕ Add Job"
5. Repeat for each job you're interested in

**Option B: Batch JSON Upload**
1. Go to "Upload JSON" tab
2. Prepare a JSON file like this:
```json
[
  {
    "company_name": "Google",
    "job_title": "Software Engineer",
    "job_url": "https://...",
    "description": "..."
  },
  {
    "company_name": "Microsoft",
    "job_title": "Product Manager"
  }
]
```
3. Upload the file
4. All jobs will be added at once

### Step 3: Configure Message Settings

In the sidebar, customize:
- **Tone**: Professional, Friendly, Formal, or Enthusiastic
- **Channel**: LinkedIn, Email, or Generic
- **Length**: Short, Medium, or Long

### Step 4: Process Jobs

1. Ensure your CV is uploaded ✓
2. Ensure you have at least one job ✓
3. Click "🚀 Start Processing"
4. Watch the progress bar as each job is processed
5. Wait for all jobs to complete

**Processing includes:**
- Searching for HR contacts at each company
- Extracting contact information (name, role, LinkedIn profile)
- Generating personalized outreach message using your CV
- Providing reasoning for contact selection

### Step 5: View Results

Each result shows:
- **Job Details**: Company, title, URL
- **HR Contact**: Name, role, LinkedIn profile, confidence score
- **Reasoning**: Why this contact is relevant
- **Outreach Message**: Personalized message ready to copy

**Actions:**
- Click each result to expand full details
- Copy messages directly from text boxes
- Review reasoning to understand contact relevance

### Step 6: Download Results

**CSV Export** (Recommended for CRM)
- Contains: Company, Title, Contact Info, Outreach Message
- Perfect for importing into Salesforce, HubSpot, etc.
- Messages truncated to 500 chars (full version in app)

**JSON Export** (For Developers)
- Full structured data
- Includes all fields and metadata
- Easy to process programmatically

## Configuration

### AWS Credentials

The web UI uses the same AWS configuration as the CLI:

```bash
# Set in .env file
AWS_REGION=eu-west-1
BEDROCK_MODEL_ID=eu.anthropic.claude-3-5-sonnet-20240620-v1:0
TAVILY_API_KEY=tvly-dev-...

# Or use AWS credentials file
~/.aws/credentials
~/.aws/config
```

The sidebar shows configuration status:
- ✓ Green: AWS configured correctly
- ✗ Red: Configuration error (check .env)

### Message Settings

**Tone Options:**
- **Professional**: Formal, business-appropriate
- **Friendly**: Warm but still professional
- **Formal**: Very traditional, conservative
- **Enthusiastic**: Energetic and passionate

**Channel Options:**
- **LinkedIn**: Short, optimized for InMail (< 300 words)
- **Email**: Includes subject line and greeting
- **Generic**: Versatile for any platform

**Length Options:**
- **Short**: Brief and concise (1-2 paragraphs)
- **Medium**: Balanced detail (3-4 paragraphs)
- **Long**: Comprehensive (5+ paragraphs)

## Technical Details

### Architecture

```
Web UI (Streamlit)
    ↓
Session State Management
    ↓
┌─────────────────┬─────────────────┐
│   CV Parser     │  Job Posting    │
│   (PyPDF2/docx) │  Management     │
└────────┬────────┴────────┬────────┘
         ↓                 ↓
    Orchestrator (process_batch_job)
         ↓
    ┌────────────────────────┐
    │  Agent Runtime         │
    │  (AWS Bedrock)         │
    └──────┬─────────────────┘
           ↓
    ┌──────────────┬─────────────────┐
    │ HR Contact   │ Message         │
    │ Discovery    │ Generation      │
    └──────────────┴─────────────────┘
           ↓
    Search Results + Outreach Messages
```

### File Processing

**CV Parsing:**
1. Upload file → BytesIO buffer
2. Detect format from extension
3. Extract raw text (PDF: PyPDF2, DOCX: python-docx, TXT: direct)
4. Parse structured fields using regex patterns
5. Return CVProfile model

**Batch Processing:**
1. Create BatchJob with all job postings
2. Pass CV profile to orchestrator
3. For each job:
   - Find HR contact (AWS Bedrock + Tavily)
   - Generate message (AWS Bedrock with CV context)
   - Store result with message
4. Return completed batch

### State Management

Streamlit session state stores:
- `cv_profile`: Parsed CV data
- `job_postings`: List of jobs to process
- `batch_results`: Processing results
- `processing`: Boolean flag
- `message_tone/channel/length`: User preferences

## Troubleshooting

### "AWS configuration error"

**Problem**: AWS credentials not found or invalid

**Solutions:**
1. Check `.env` file exists with correct values
2. Verify AWS credentials in `~/.aws/credentials`
3. Ensure Bedrock model access is enabled in AWS Console
4. Try running: `aws bedrock list-foundation-models --region eu-west-1`

### "Failed to parse CV"

**Problem**: CV file can't be read

**Solutions:**
1. Ensure file is not corrupted
2. Try converting to TXT first
3. Check file size (< 10MB recommended)
4. For PDF: ensure it's text-based, not scanned image

### "No contacts found"

**Problem**: Agent can't find HR contacts

**Solutions:**
1. Check Tavily API key in `.env`
2. Try more well-known companies
3. Add job description for better context
4. Check `agent_execution.log` for details

### "Processing takes too long"

**Problem**: Batch processing is slow

**Reasons:**
- Rate limiting: 2-second delay between jobs
- Message generation adds ~5-10s per job
- Web search can take 10-15s per job

**Optimizations:**
- Process smaller batches (5-10 jobs)
- Use CLI for very large batches
- Check your internet connection

## Best Practices

### CV Preparation
✓ Use clear section headers (SKILLS, EXPERIENCE, EDUCATION)
✓ Include specific technologies and tools
✓ List recent experience first
✓ Keep formatting simple
✗ Avoid heavy graphics or unusual layouts
✗ Don't use scanned images

### Job Selection
✓ Focus on roles that match your experience
✓ Include job descriptions when available
✓ Add job URLs for reference
✓ Process 5-10 jobs at a time for best results
✗ Don't add jobs you're not serious about
✗ Avoid very obscure or outdated positions

### Message Customization
✓ Review generated messages before sending
✓ Add personal touches or specific details
✓ Adjust tone based on company culture
✓ Proofread for any errors
✗ Don't send messages without reviewing
✗ Avoid using the exact same message for everyone

## Examples

### Example Workflow

1. Upload CV: `john_doe_resume.pdf`
2. Add 5 jobs manually from job boards
3. Set tone: Professional, channel: LinkedIn
4. Click "Start Processing"
5. Wait ~3-5 minutes for completion
6. Review all contacts and messages
7. Copy messages to LinkedIn InMail
8. Download CSV for tracking in spreadsheet

### Example Generated Message

```
Hi [Contact Name],

I hope this message finds you well. I came across the [Job Title] position
at [Company] and was immediately drawn to the opportunity to contribute to
your team's work in [relevant area].

With 5+ years of experience in [relevant skills from CV], I've developed a
strong foundation in [key competencies]. Most recently at [Your Company],
I [relevant achievement that matches the job].

I'd love to learn more about this role and discuss how my background in
[specific skills] could benefit your team. Would you be open to a brief
conversation?

Thank you for considering my application.

Best regards,
[Your Name]
```

## FAQ

**Q: Can I use the web UI without AWS credentials?**
A: No, the agent requires AWS Bedrock access. Sign up for AWS and enable Bedrock in your region.

**Q: Is my CV data stored anywhere?**
A: No, CV data is only processed in memory during your session. Nothing is stored or sent anywhere except to AWS Bedrock for message generation.

**Q: Can I edit generated messages?**
A: Yes! Messages are shown in editable text boxes. Copy, modify, and use as you see fit.

**Q: How accurate is the CV parser?**
A: The parser uses regex patterns and works well with standard CV formats. Complex layouts may not parse perfectly, but you can still use the system.

**Q: Can I cancel processing mid-way?**
A: No, once processing starts it must complete. Process smaller batches if you need flexibility.

**Q: What's the cost of using this?**
A: AWS Bedrock charges per API call. Claude 3.5 Sonnet costs ~$3 per million tokens. Processing 10 jobs with messages costs approximately $0.10-0.30.

## Support

For issues or questions:
- Check logs: `agent_execution.log`
- GitHub Issues: https://github.com/isaacng924/Ai-agent/issues
- AWS Bedrock Docs: https://docs.aws.amazon.com/bedrock/

---

**Happy job hunting! 🚀**
