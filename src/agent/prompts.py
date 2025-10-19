"""Prompt templates for the Job Connector Agent."""

# System prompt for the agent's primary role
SYSTEM_PROMPT = """You are an expert HR contact discovery assistant. Your role is to help job seekers identify the most relevant HR contacts and recruiters for specific job opportunities.

You have access to web search tools to find HR professionals at target companies. Your goal is to:
1. Search for HR contacts, recruiters, or talent acquisition professionals at the specified company
2. Identify the most relevant contact based on the job title and company
3. Provide clear reasoning for why this contact is appropriate
4. Return structured data with confidence scores

Always prioritize:
- Current employees over former employees
- Recruiters who specialize in the relevant department (e.g., Engineering, Sales)
- Contacts with recent activity or public profiles
- Verified LinkedIn profiles when available

When you cannot find a suitable contact:
- Explain what you searched for and why results were insufficient
- Provide alternative suggestions (e.g., company careers page, general recruiting email)
- Be honest about limitations rather than making up information
"""

# Template for contact discovery task
CONTACT_DISCOVERY_PROMPT = """Find the most relevant HR contact or recruiter for the following job opportunity:

**Company:** {company_name}
**Job Title:** {job_title}
{description_section}

Use the web search tool to find:
1. Current recruiters or HR professionals at {company_name}
2. Talent acquisition team members who handle {job_category} roles
3. LinkedIn profiles of relevant contacts

Return your findings in this structure:
- Contact name and role
- Profile URL (if available)
- Confidence score (0.0-1.0)
- Reasoning for why this contact is most relevant
- Source of information (LinkedIn, company website, etc.)

If no suitable contact is found, explain what you searched and suggest alternatives.
"""

# Template for contact reasoning (User Story 2)
CONTACT_REASONING_PROMPT = """Analyze the following HR contact and explain why they are the best match for this job opportunity:

**Job Details:**
- Company: {company_name}
- Job Title: {job_title}
- Description: {description}

**Contact Found:**
- Name: {contact_name}
- Role: {contact_role}
- Profile: {profile_url}
- Source: {source}

Provide detailed reasoning that covers:
1. **Relevance:** Why this person is well-suited for this specific role
2. **Recency:** Recent activity or posts related to hiring (if available)
3. **Department Alignment:** How their focus area matches the job
4. **Confidence Factors:** What makes you confident in this match

Your reasoning should be 2-4 sentences and help the job seeker understand why reaching out to this contact makes sense.
"""

# Template for message generation (User Story 4)
MESSAGE_GENERATION_PROMPT = """Generate a personalized outreach message for the following context:

**Job Seeker Profile:**
{job_seeker_info}

**Target Job:**
- Company: {company_name}
- Job Title: {job_title}
- Description: {description}

**HR Contact:**
- Name: {contact_name}
- Role: {contact_role}
- Profile: {profile_url}

**Message Requirements:**
- Tone: {tone}
- Channel: {channel}
- Length: {length}

Create a {tone} message that:
1. Introduces the job seeker professionally
2. Expresses genuine interest in the specific role
3. Highlights 1-2 relevant skills or experiences
4. Includes a clear call-to-action
5. Maintains appropriate formality for {channel}

{channel_specific_instructions}

Return the message as plain text, ready to copy and send.
"""


def format_contact_discovery_prompt(
    company_name: str, job_title: str, description: str = None
) -> str:
    """
    Format the contact discovery prompt with job details.

    Args:
        company_name: Name of the target company
        job_title: Job title to search for
        description: Optional job description for context

    Returns:
        Formatted prompt string
    """
    description_section = ""
    if description:
        description_section = f"**Job Description:** {description[:500]}"

    # Infer job category from title for better search targeting
    job_category = _infer_job_category(job_title)

    return CONTACT_DISCOVERY_PROMPT.format(
        company_name=company_name,
        job_title=job_title,
        description_section=description_section,
        job_category=job_category,
    )


def format_contact_reasoning_prompt(
    company_name: str,
    job_title: str,
    description: str,
    contact_name: str,
    contact_role: str,
    profile_url: str,
    source: str,
) -> str:
    """
    Format the contact reasoning prompt.

    Args:
        company_name: Target company
        job_title: Job title
        description: Job description
        contact_name: Name of HR contact
        contact_role: Role of HR contact
        profile_url: Profile URL
        source: Source where contact was found

    Returns:
        Formatted prompt string
    """
    return CONTACT_REASONING_PROMPT.format(
        company_name=company_name,
        job_title=job_title,
        description=description or "Not provided",
        contact_name=contact_name,
        contact_role=contact_role,
        profile_url=profile_url or "Not available",
        source=source,
    )


def format_message_generation_prompt(
    job_seeker_info: str,
    company_name: str,
    job_title: str,
    description: str,
    contact_name: str,
    contact_role: str,
    profile_url: str,
    tone: str = "professional",
    channel: str = "linkedin",
    length: str = "medium",
) -> str:
    """
    Format the message generation prompt.

    Args:
        job_seeker_info: Background info about the job seeker
        company_name: Target company
        job_title: Job title
        description: Job description
        contact_name: HR contact name
        contact_role: HR contact role
        profile_url: HR contact profile
        tone: Message tone (professional, friendly, formal, enthusiastic)
        channel: Delivery channel (linkedin, email, generic)
        length: Message length (short, medium, long)

    Returns:
        Formatted prompt string
    """
    channel_instructions = {
        "linkedin": "Keep the message concise for LinkedIn InMail (under 300 words). Use a friendly but professional tone.",
        "email": "Format as a professional email with subject line. Include greeting and signature placeholders.",
        "generic": "Create a versatile message that could be adapted for multiple channels.",
    }

    return MESSAGE_GENERATION_PROMPT.format(
        job_seeker_info=job_seeker_info,
        company_name=company_name,
        job_title=job_title,
        description=description or "Not provided",
        contact_name=contact_name,
        contact_role=contact_role,
        profile_url=profile_url or "Not available",
        tone=tone,
        channel=channel,
        length=length,
        channel_specific_instructions=channel_instructions.get(
            channel, channel_instructions["generic"]
        ),
    )


def _infer_job_category(job_title: str) -> str:
    """
    Infer job category from title for better search targeting.

    Args:
        job_title: Job title string

    Returns:
        Inferred category (e.g., "Engineering", "Sales", "Marketing")
    """
    title_lower = job_title.lower()

    if any(
        keyword in title_lower
        for keyword in ["engineer", "developer", "software", "technical", "data"]
    ):
        return "Engineering"
    elif any(keyword in title_lower for keyword in ["sales", "account", "business"]):
        return "Sales"
    elif any(keyword in title_lower for keyword in ["market", "brand", "content"]):
        return "Marketing"
    elif any(keyword in title_lower for keyword in ["product", "pm"]):
        return "Product"
    elif any(keyword in title_lower for keyword in ["design", "ux", "ui"]):
        return "Design"
    elif any(keyword in title_lower for keyword in ["hr", "people", "talent"]):
        return "Human Resources"
    else:
        return "General"
