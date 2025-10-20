# AI Job Connector Agent - Demo Script

## 🎯 Quick Demo (2 Minutes)

### Opening (10 seconds)
**[Show GitHub README with live demo link]**

"Hi! I'm presenting the AI Job Connector Agent for the AWS AI Agent Hackathon. This AI agent automates one of the most time-consuming parts of job hunting: finding the right HR contacts and writing personalized outreach messages."

### Problem Statement (15 seconds)
**[Switch to web UI]**

"Job seekers typically spend 15-30 minutes per job posting manually searching LinkedIn for recruiters, guessing email formats, and writing generic messages. Our AI agent does this automatically in under 60 seconds."

### Live Demo - Part 1: Setup (30 seconds)
**[Navigate to live demo URL]**

"This is running live on AWS ECS Fargate with an Application Load Balancer. Let me show you how it works."

**[Upload CV]**
- Click "Browse files" or drag-and-drop
- Upload sample CV

"First, I upload my CV. The agent uses Claude 3.5 Sonnet on Amazon Bedrock to parse and understand my skills and experience."

**[Add job posting]**
- Enter company: "Amazon Web Services"
- Enter title: "Cloud Solutions Architect"
- Click "Add Job"

"Then I add a job I'm interested in - let's say Cloud Solutions Architect at AWS."

### Live Demo - Part 2: Processing (45 seconds)
**[Click "Start Processing"]**

"Now I click Start Processing, and watch what happens:"

**[Point to progress indicators as they appear]**

"The AI agent is working autonomously:
1. **Web Search** - It's searching LinkedIn, company pages, and job boards for relevant HR contacts using the Tavily API
2. **Contact Validation** - Claude analyzes each result and selects the most relevant recruiter
3. **Message Generation** - It crafts a personalized message based on my CV and the job requirements"

**[Wait for results to appear - usually 30-60 seconds]**

### Results (20 seconds)
**[Show the results]**

"And here we have it! The agent found [Name], a [Role] at AWS, with their LinkedIn profile. It also generated a personalized message that:
- Highlights my relevant experience from my CV
- References the specific role requirements
- Uses a professional but friendly tone
- Is ready to copy-paste into LinkedIn"

**[Scroll to show message]**

"I can now copy this message and send it immediately, or export all results to CSV for my CRM."

### Technical Highlights (10 seconds)
**[Switch back to GitHub - show architecture diagram]**

"Under the hood, this runs on:
- **Amazon Bedrock** with Claude 3.5 Sonnet for reasoning
- **ECS Fargate** for serverless container orchestration
- **Application Load Balancer** with auto-scaling
- **AWS CDK** for complete infrastructure as code"

### Closing (10 seconds)
**[Show README with badges and live link]**

"The entire application is open source, deployed to production, and ready to use. Thank you!"

---

## 🎬 Detailed Demo (5 Minutes)

### Opening (20 seconds)
**[Show GitHub README]**

"Good [morning/afternoon]! I'm [Your Name], and I'm excited to present the AI Job Connector Agent, built for the AWS AI Agent Hackathon 2025.

This project solves a real problem I personally experienced: the tedious process of finding HR contacts and writing personalized outreach messages for job applications."

### Problem Deep Dive (30 seconds)
**[Show problem section of README]**

"Here's the problem: Job seekers waste hours on each application doing manual research:
- ❌ Searching LinkedIn for the right recruiter - often finding generic HR emails
- ❌ Researching company culture and hiring managers
- ❌ Writing personalized messages that stand out
- ❌ Tracking everything in spreadsheets

For 10 job applications, this is **3-5 hours of repetitive work**. And let's be honest - by job #8, your messages aren't very personalized anymore."

### Solution Overview (20 seconds)
**[Scroll to Key Features]**

"Our solution: An autonomous AI agent that:
1. Finds the most relevant HR contact for each job
2. Explains WHY they selected that person
3. Generates personalized messages based on your CV
4. Processes 10 jobs in under 5 minutes
5. Exports to CSV for CRM integration

And it's running live on AWS right now. Let me show you."

### Live Demo - Part 1: Architecture (30 seconds)
**[Navigate to live demo URL - keep network tab open if doing screen recording]**

"Here's our production deployment on AWS ECS Fargate. I'll walk through what's happening behind the scenes as we use it.

**[Show URL in browser]**

The URL you see is from our Application Load Balancer in eu-west-1. Behind this, we have:
- ECS Fargate tasks running our Streamlit container
- Auto-scaling from 1 to 25 instances based on traffic
- CloudWatch Logs capturing all events
- And most importantly, Amazon Bedrock providing the AI reasoning"

### Live Demo - Part 2: CV Upload (40 seconds)
**[Upload CV - use a real-looking one if possible]**

"First step: Upload a CV. I'll use this sample software engineering CV."

**[Drag and drop the file]**

"As soon as I upload it, the application sends it to our backend service, which uses Claude 3.5 Sonnet to extract:
- Professional experience and years
- Technical skills
- Education background
- Key achievements

This context is crucial for generating personalized messages later."

**[Show parsed CV information if your UI displays it]**

"You can see it's extracted my skills: Python, AWS, Docker, etc. This takes about 2-3 seconds."

### Live Demo - Part 3: Add Jobs (40 seconds)
**[Add multiple jobs to show batch capability]**

"Now I'll add some job postings. You can add them manually like this..."

**[Add first job]**
- Company: "Amazon Web Services"
- Title: "Senior Cloud Architect"
- Click "Add Job"

"Or import a JSON file with 10-50 jobs at once."

**[Click JSON import button]**
- Show the JSON import option
- "I'll skip this for time, but the format is simple: just company and title for each job."

**[Add 1-2 more jobs manually]**
- Company: "Anthropic"
- Title: "AI Safety Researcher"
- Add job

"Let me add one more - Anthropic is doing amazing work in AI safety."

**[Show job list]**

"Great! I now have 2-3 jobs queued up."

### Live Demo - Part 4: Processing (90 seconds)
**[Click "Start Processing" - this is the star of the show!]**

"Now here's where the magic happens. I click 'Start Processing' and our AI agent takes over."

**[Watch progress indicators]**

"What's happening right now:

**Phase 1: Web Search**
- The agent is calling the Tavily web search API
- It's searching LinkedIn profiles, company career pages, and job boards
- Looking for terms like 'recruiter', 'talent acquisition', 'hiring manager' at AWS

**Phase 2: Intelligent Filtering**
- Claude 3.5 Sonnet analyzes each search result
- It's asking itself: 'Is this person actually relevant?'
- It considers: job title, company, LinkedIn profile activity, role description
- It assigns a confidence score from 0 to 1.0

**Phase 3: Reasoning**
This is my favorite part - the agent doesn't just pick a contact, it explains WHY.

**[Point to reasoning when it appears]**

See this reasoning: '[Read the actual reasoning displayed]'

This transparency is crucial - you can verify the agent's logic before sending a message.

**Phase 4: Message Generation**
- Now it's crafting a personalized LinkedIn message
- It references specific skills from my CV
- It mentions the role requirements
- It keeps it concise (under 300 characters for LinkedIn)"

**[Wait for all results]**

"And... done! About 60 seconds total for 2-3 jobs."

### Live Demo - Part 5: Results (40 seconds)
**[Show first result in detail]**

"Let's look at the first result for AWS Cloud Architect:

**Contact Found:**
- Name: [Read name]
- Role: [Read role]
- LinkedIn: [Show LinkedIn URL]
- Confidence: [Read confidence score]

**Generated Message:**
[Read first 2-3 sentences of the message]

Notice how it:
1. Opens with a specific reason for reaching out
2. Mentions my relevant AWS experience from my CV
3. References the Cloud Architect role specifically
4. Keeps it professional but friendly
5. Has a clear call-to-action

I can copy this right now and send it on LinkedIn."

**[Click "Copy Message" button if you have one]**

"One click to copy, paste into LinkedIn, send. Done."

### Export Capability (20 seconds)
**[Show export options]**

"If I'm processing 50 jobs, I can export everything:

**JSON Format** - For developers who want to build integrations
**CSV Format** - For CRM systems like Salesforce or HubSpot

The CSV includes: Company, Job Title, Contact Name, Contact Role, LinkedIn URL, Message, Confidence Score."

**[Click download CSV]**

"Perfect for tracking in a spreadsheet or importing into your ATS."

### Technical Deep Dive (40 seconds)
**[Switch to GitHub - show architecture diagram]**

"Let me show you the technical architecture that makes this possible:

**AWS Services:**
- **Amazon Bedrock**: Claude 3.5 Sonnet for all AI reasoning
- **ECS Fargate**: Runs our containerized Streamlit app
- **Application Load Balancer**: Health checks and traffic distribution
- **CloudWatch Logs**: Centralized logging for debugging
- **Amazon ECR**: Stores our Docker images
- **AWS CDK**: Everything deployed as infrastructure as code

**Why ECS Fargate over App Runner?**
Great question! We initially tried App Runner but hit a subscription requirement. ECS gave us:
- More control over networking and security groups
- Better integration with VPC and other AWS services
- More flexibility for future microservices
- It's a more production-grade architecture that impresses judges

**Key Design Decisions:**
1. **Autonomous Agent Pattern**: The AI makes decisions without human intervention
2. **Gateway Primitive**: Clean separation between agent logic and tool integration
3. **Reasoning Transparency**: Agent explains its decisions
4. **Batch Processing**: Concurrent processing for efficiency
5. **Export Flexibility**: JSON for developers, CSV for business users"

### AWS Hackathon Compliance (20 seconds)
**[Show AWS Hackathon Compliance section]**

"This meets all hackathon requirements:

✅ **LLM on Bedrock**: Claude 3.5 Sonnet
✅ **AgentCore Framework**: Gateway primitive for tool integration
✅ **Reasoning LLMs**: Autonomous decision-making with explanations
✅ **Real-world Use Case**: Solves actual job seeker pain point
✅ **Production Deployment**: Live on AWS right now
✅ **Infrastructure as Code**: Complete CDK implementation"

### Demo the Code (Optional - 30 seconds)
**[Show key code snippets if time allows]**

"Quick code walkthrough:

**[Show `src/agent/orchestrator.py`]**
This is our AgentCore implementation with the Gateway primitive for tool calling.

**[Show `infra/cdk/stacks/ecs_fargate_stack.py`]**
Here's our ECS Fargate stack - VPC, load balancer, auto-scaling, all defined in Python CDK.

**[Show `src/services/message_generator.py`]**
This service takes the CV profile and job details to generate personalized messages."

### Impact & Metrics (20 seconds)
**[Show Success Metrics section]**

"Real impact:
- **Time Savings**: 15+ minutes saved per job posting
- **Success Rate**: 80%+ contact discovery accuracy
- **Speed**: Under 60 seconds per job
- **Batch Efficiency**: 10 jobs in under 5 minutes
- **Cost**: About $15-20/month to run on AWS with auto-scaling"

### Future Roadmap (15 seconds)
"Next steps for this project:
1. Email discovery and validation
2. Follow-up message sequences
3. Integration with LinkedIn API for auto-sending
4. Analytics dashboard showing response rates
5. Chrome extension for one-click processing from LinkedIn job pages"

### Closing (15 seconds)
**[Show GitHub repo with star button visible]**

"The entire project is open source on GitHub. The infrastructure code, the agent logic, the web UI - everything is there.

You can:
- Try the live demo right now
- Deploy your own instance with one command
- Contribute or fork for your own use case

Thank you! Happy to answer any questions."

---

## 📝 Tips for Your Demo

### Before Recording/Presenting:

1. **Practice Multiple Times**
   - Record yourself and watch it back
   - Aim for natural, conversational tone
   - Don't read from a script - use it as a guide

2. **Prepare Your Environment**
   - Clear browser cache and history
   - Close unnecessary tabs
   - Use a clean, professional browser profile
   - Test the live demo beforehand
   - Have backup screenshots in case the demo breaks

3. **Have a Backup Plan**
   - Take screenshots of each step
   - Record a backup video of the demo working
   - Have the architecture diagram ready to show

4. **Timing Considerations**
   - 2-min version: Focus on problem → demo → impact
   - 5-min version: Add technical architecture and code
   - Practice to stay within time limit

### During Demo:

1. **Start Strong**
   - State the problem clearly in first 15 seconds
   - Show the live demo immediately
   - Don't spend too long on intro slides

2. **Show, Don't Tell**
   - Let the AI agent actually process
   - Show real results, not pre-recorded videos
   - Point out specific features as they happen

3. **Highlight AWS Integration**
   - Mention Bedrock, ECS, CDK throughout
   - Show you understand AWS architecture
   - Explain why you chose specific services

4. **Handle Issues Gracefully**
   - If demo breaks: "This is a live production system, so let me show you screenshots of what normally happens..."
   - If it's slow: "While we wait, let me explain what's happening under the hood..."
   - If API fails: "This shows the importance of error handling - in production we'd retry with exponential backoff"

### Key Phrases to Use:

- "This is running **live on AWS** right now"
- "The agent is making **autonomous decisions** using Claude"
- "Notice the **reasoning transparency** here"
- "All deployed with **infrastructure as code**"
- "This solves a **real problem** I personally experienced"
- "**Production-ready** with auto-scaling and monitoring"

### What NOT to Do:

- ❌ Don't apologize for bugs (just explain them)
- ❌ Don't spend too long on non-AWS tech
- ❌ Don't read from notes the whole time
- ❌ Don't skip showing the live demo
- ❌ Don't forget to mention it's production-deployed
- ❌ Don't overcomplicate the explanation

---

## 🎥 Video Recording Tips

### Setup:
```bash
# Test the demo first
open http://AIJobC-Strea-WrYDOzMzyH2J-1101858695.eu-west-1.elb.amazonaws.com

# Have these ready to show:
- GitHub README
- Live demo URL
- Architecture diagram
- Sample CV for upload
- 2-3 job postings to add
```

### Recording Tools:
- **Loom** (easiest, web-based)
- **OBS Studio** (more professional)
- **QuickTime** (Mac, simple)
- **Zoom** (record yourself presenting)

### Video Checklist:
- [ ] 1080p resolution minimum
- [ ] Clear audio (use a decent microphone)
- [ ] Show your face (optional but helps connect with judges)
- [ ] Keep it under 5 minutes
- [ ] Upload to YouTube (unlisted or public)
- [ ] Add captions/subtitles
- [ ] Include GitHub link in video description

---

## 🏆 Judge Appeal Points

Emphasize these throughout your demo:

1. **It Actually Works**
   - "This isn't just code - it's live on AWS"
   - "You can try it right now at [URL]"

2. **Production-Grade**
   - "Complete infrastructure as code"
   - "Auto-scaling, health checks, monitoring"
   - "Security best practices: IAM, VPC, secrets management"

3. **Real Problem, Real Solution**
   - "I personally spent hours doing this manually"
   - "This saves 15+ minutes per job posting"
   - "80%+ success rate finding contacts"

4. **AWS Expertise**
   - "Uses 6 different AWS services"
   - "Deployed with AWS CDK in Python"
   - "Shows understanding of ECS, ALB, Bedrock"

5. **Intelligent Agent Design**
   - "Autonomous decision-making"
   - "Reasoning transparency"
   - "Context-aware message generation"

---

Good luck with your demo! 🚀
