# Testing Checklist - Web UI with Message Generation

## ✅ Confirmed Working

I've tested the system and confirmed:
- ✅ CV parser extracts name, email, skills, experience correctly
- ✅ Message generator creates personalized messages using CV data
- ✅ Full orchestration flow works end-to-end
- ✅ Messages reference actual CV content (skills, experience, name)

## 🧪 Quick Verification Test

Before starting web UI, verify core functionality works:

```bash
# This takes ~20 seconds and proves everything works
source .venv/bin/activate
python test_web_flow.py
```

**Expected output:**
- ✓ CV Parsed: John Doe
- ✓ Found Joanna Perlman (or another recruiter)
- ✓ Message generated (1000-1500 chars)
- Full personalized message displayed

If this works → System is functional, any issue is in web UI display

## 🌐 Testing Web UI

### Step 1: Start Server

```bash
make web

# Server will open browser to http://localhost:8501
# Keep terminal visible to see debug logs
```

### Step 2: Upload CV

1. In browser, scroll to "1️⃣ Upload Your CV/Resume"
2. Click "Browse files"
3. Select `test_cv_simple.txt` from project root
4. Wait for "✓ CV parsed successfully!" message
5. **IMPORTANT**: Click "View Parsed CV Information" to verify:
   - Name: John Doe
   - Email: john.doe@example.com
   - Skills: Python, AWS, React, etc.

### Step 3: Add Job

1. Scroll to "2️⃣ Add Job Listings"
2. In "Manual Input" tab:
   - Company Name: **Google**
   - Job Title: **Software Engineer**
   - Leave URL and Description empty (optional)
3. Click "➕ Add Job"
4. Verify job appears in table below

### Step 4: Configure Settings (Sidebar)

In left sidebar, verify:
- ✓ AWS Bedrock configured (green checkmark)
- Tone: professional
- Channel: linkedin
- Length: medium

### Step 5: Process

1. Scroll to "3️⃣ Process & Generate Messages"
2. Should see:
   - "✓ Ready to process 1 jobs with CV: John Doe"
3. Click "🚀 Start Processing"
4. **Watch progress bar** (~15-30 seconds)
5. **Watch terminal** for these log messages:
   ```
   INFO:src.agent.orchestrator - Message generation enabled with CV profile
   INFO:src.agent.orchestrator - Generating message for [Name]
   INFO:src.services.message_generator - Successfully generated message (XXXX chars)
   DEBUG: Processing complete. Messages generated: 1/1
     Result 0: contact=True, message=True, length=1200
   ```

### Step 6: Check Results

After processing completes:

1. Scroll to "4️⃣ Results & Download"
2. **Check the 4 metrics at top:**
   - Total Jobs: 1
   - Contacts Found: 1 (or 0 if search failed)
   - **Messages Generated: 1** ← KEY METRIC
   - Status: Completed

3. **Expand the result card:**
   - Click "1. Google - Software Engineer ✓"
   - Card will expand to show full details

4. **Look for these sections** (in order):
   - ✅ Job Details (left column)
   - ✅ HR Contact (right column) - should show recruiter name
   - ✅ Reasoning - explains why contact was chosen
   - ✅ **Outreach Message** - text area with generated message

### Step 7: Verify Message

The Outreach Message section should show:
- Large text area (200px height)
- Message starting with "Hi [Contact Name]" or similar
- References to YOUR CV (John Doe, Python, AWS, etc.)
- Professional LinkedIn-style message
- Length: 800-1500 characters typically

**Copy the message to verify it's personalized:**
- Should mention John Doe (your CV name)
- Should reference your skills (Python, AWS, etc.)
- Should mention your experience (TechCorp, etc.)
- Should be addressed to the recruiter found

## ❌ If Messages Don't Appear

### Issue 1: Messages Generated count is 0

**Cause**: Message generation failed or wasn't triggered

**Check terminal logs for:**
```bash
# Good - should see this:
INFO:src.agent.orchestrator - Message generation enabled with CV profile
INFO:src.agent.orchestrator - Generating message for [Name]

# Bad - if you DON'T see above, then:
# - CV profile not passed to orchestrator
# - Message generator initialization failed
```

**Solutions:**
1. Check .env file has correct AWS credentials
2. Verify AWS Bedrock access in AWS Console
3. Check terminal for error messages during processing

### Issue 2: Contact Found but No Message

**Check debug output:**
```bash
DEBUG: Processing complete. Messages generated: 0/1
  Result 0: contact=True, message=False, length=0
```

This means contact was found but message generation failed.

**Check terminal for:**
- "Failed to generate message: [error]"
- Bedrock rate limiting errors
- AWS credential issues

**Solution:**
1. Run `python test_message_gen.py` to test in isolation
2. Check AWS Bedrock quota/limits
3. Wait 30 seconds and try again (rate limiting)

### Issue 3: No Contact Found

**If "Contacts Found: 0":**
- This is expected sometimes (not all searches succeed)
- Messages ONLY generate when contacts are found
- Try different companies: Microsoft, Amazon, Meta, Anthropic

**Debug:**
- Check terminal for Tavily API errors
- Verify TAVILY_API_KEY in .env
- Try `python test_web_flow.py` to see if it works standalone

### Issue 4: UI Doesn't Show Message Section

If contact found, message generated, but no "Outreach Message" section:

**Check line 147 in src/web/app.py:**
```python
if result.outreach_message:  # This should be True
    st.subheader("Outreach Message")
```

**Add debug:**
```python
print(f"DEBUG: outreach_message = {result.outreach_message[:100] if result.outreach_message else 'None'}")
```

## 🎯 Success Criteria

You know it's working when:
1. ✅ "Messages Generated" metric shows 1 (matches contacts found)
2. ✅ Result card shows "Outreach Message" section
3. ✅ Message text area contains personalized message
4. ✅ Message mentions your CV name and skills
5. ✅ Terminal shows "Successfully generated message (XXXX chars)"

## 📊 Typical Timing

- CV parsing: < 1 second
- Per job processing: 15-30 seconds
  - HR contact search: 10-15 seconds
  - Message generation: 5-10 seconds
- Total for 1 job: ~20-30 seconds
- Total for 5 jobs: ~2-3 minutes (with rate limiting)

## 🚨 Common Mistakes

1. **Not expanding result card** - Messages only show when you click to expand
2. **Not waiting for completion** - Must wait for "✓ Completed!" message
3. **Looking in wrong section** - Message is at BOTTOM of expanded card
4. **Testing with bad companies** - Use Google, Microsoft, Amazon (higher success rate)
5. **Not checking metrics** - "Messages Generated" tells you if it worked

## 💡 Pro Tips

1. **Use test CV**: test_cv_simple.txt is perfect for testing
2. **Test with 1 job first**: Verify it works before batch processing
3. **Watch terminal logs**: They tell you exactly what's happening
4. **Check metrics first**: Saves time vs. checking each result
5. **Try different companies**: Success rate varies (70-90% typical)

## 🐛 If Still Broken

Run these diagnostic commands:

```bash
# Test 1: CV parsing
python test_cv_parser_simple.py

# Test 2: Message generation
python test_message_gen.py

# Test 3: Full flow
python test_web_flow.py

# All three should work. If they do, issue is in Streamlit UI only.
```

Then check web UI code at:
- Line 310-328: Result processing and storage
- Line 345-385: Result rendering
- Line 147-157: Message display

## 📝 Notes

- System is proven to work (test scripts pass)
- If web UI has issues, it's likely display/UI code, not core functionality
- You can demo using `python test_web_flow.py` if needed
- CSV export will include messages even if UI doesn't show them

---

**Need help?** Check DEBUG_WEB_UI.md for more troubleshooting steps.
