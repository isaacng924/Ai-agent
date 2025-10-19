# Security Guidelines

## Overview

This document outlines the security practices and considerations for the AI Job Connector Agent.

## ✅ Pre-Push Security Checklist

Before pushing to GitHub, ensure you complete these steps:

- [x] `.env` file is NOT committed (verified - properly gitignored)
- [ ] **IMPORTANT**: Revoke the Tavily API key `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`
- [ ] Generate a new Tavily API key at https://tavily.com
- [x] `.gitignore` properly excludes sensitive files
- [x] No API keys or secrets in source code
- [x] `.env.example` contains only placeholder values
- [ ] AWS credentials are not hardcoded (verified - uses boto3 credential chain)

## 🔒 Credential Management

### API Keys

**Never commit these files:**
- `.env` - Contains real API keys
- `*_results.json` - May contain sensitive search results
- `batch_jobs.json` - May contain real company data

**Safe to commit:**
- `.env.example` - Template with placeholders only
- Source code in `src/` - No hardcoded secrets
- Documentation and configuration files

### AWS Credentials

This project uses AWS Bedrock. Credentials should be managed via:

1. **Development**: AWS CLI profiles (`~/.aws/credentials`)
2. **Production**: IAM roles or AWS Secrets Manager

**Never** hardcode AWS access keys in the code.

## 🛡️ Security Best Practices

### 1. Environment Variables

Always load sensitive configuration from environment variables:

```python
# Good ✅
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Bad ❌
TAVILY_API_KEY = "tvly-abc123..."
```

### 2. API Rate Limiting

The batch processor includes built-in rate limiting (2-second delays) to prevent:
- API throttling
- Excessive costs
- Potential abuse

### 3. Input Validation

All user inputs are validated using Pydantic models:
- Company names: 1-200 characters
- Job titles: 1-200 characters
- Search results: Limited to 50 max

### 4. Error Handling

Errors are logged but sensitive details are not exposed to end users.

## 🔐 Sensitive Data

### What This Application Handles

- **API Keys**: Tavily web search, AWS Bedrock
- **Search Results**: LinkedIn URLs, recruiter names
- **Company Data**: Company names, job titles

### Data Storage

- **Local files**: JSON output files may contain search results
- **Logs**: Application logs may contain company/job information
- **AWS**: Temporary data in Bedrock API calls

**Recommendation**: Do not commit output files or logs to version control.

## 📋 Security Maintenance

### Regular Tasks

1. **Rotate API Keys** - Every 90 days
   - Tavily: https://tavily.com
   - AWS: Use IAM role rotation

2. **Update Dependencies** - Monthly
   ```bash
   pip install --upgrade pip
   pip install --upgrade -r requirements.txt
   ```

3. **Security Scanning** - Before each release
   ```bash
   pip install pip-audit
   pip-audit
   ```

### Known Dependencies (As of 2025-10-19)

- boto3==1.40.50 (AWS SDK)
- requests==2.32.4 (HTTP client)
- pydantic==2.11.7 (Data validation)
- click==8.2.1 (CLI framework)
- rich==14.2.0 (Terminal formatting)

## 🚨 Incident Response

### If API Key is Leaked

1. **Immediately revoke** the compromised key
2. **Generate** a new key
3. **Update** `.env` file locally
4. **Monitor** API usage for suspicious activity
5. **Review** git history to ensure key wasn't committed

### If Credentials Are Compromised

1. **Rotate** AWS credentials immediately
2. **Review** CloudTrail logs for unauthorized access
3. **Check** Bedrock usage for anomalies
4. **Update** all affected systems

## 📞 Security Contacts

- **Tavily API Support**: https://tavily.com/support
- **AWS Security**: https://aws.amazon.com/security/
- **Project Issues**: https://github.com/isaacng924/Ai-agent/issues

## ✅ Security Review Status

Last security review: 2025-10-19

**Status**: PASSED with critical fixes applied

**Reviewer**: Claude Code Security Review Agent

**Findings**:
- ✅ No hardcoded secrets in source code
- ✅ `.env` properly gitignored
- ✅ Input validation implemented
- ✅ Secure AWS credential management
- ✅ Error handling sanitized

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
- [Python Security](https://python.readthedocs.io/en/stable/library/security_warnings.html)
