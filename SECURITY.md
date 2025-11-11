# Security Policy

## Supported Versions

The following versions of Krya.ai are currently being supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Known Security Considerations

### Important Security Notes

⚠️ **This application executes AI-generated code on your local machine with your user privileges.**

- Always review generated code before execution when possible
- Do not run this application with administrator/root privileges
- Be cautious with prompts that involve sensitive data or system operations
- This is a development/research tool, not intended for production use

### API Key Security

- Never commit your API keys to version control
- Store API keys in `.env` file (already in `.gitignore`)
- Use environment variables for all sensitive configuration
- Rotate your API keys periodically

### Generated Code Risks

- Generated code can access your files and system resources
- PyAutoGUI can control your mouse and keyboard
- Code execution is not sandboxed in the current version
- Always save your work in other applications before running automation

## Reporting a Vulnerability

We take security issues seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

1. **Do NOT** create a public GitHub issue for security vulnerabilities
2. Email the maintainer directly at: devdattatalele@gmail.com
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Initial Response**: Within 48 hours of your report
- **Status Update**: Weekly updates on investigation progress
- **Resolution Timeline**: 
  - Critical: 1-7 days
  - High: 7-30 days
  - Medium: 30-90 days
  - Low: Best effort basis

### After Reporting

- We will acknowledge your report and begin investigation
- We will keep you informed about our progress
- We will credit you in the security advisory (unless you prefer to remain anonymous)
- We will notify you when the vulnerability is fixed

## Security Best Practices for Users

### Setup
- [ ] Use a dedicated user account (not admin) for running Krya.ai
- [ ] Keep your API keys secure and never share them
- [ ] Use `.env` file for configuration, not hardcoded values
- [ ] Keep all dependencies up to date

### Usage
- [ ] Review generated code before execution when possible
- [ ] Don't process sensitive or confidential information
- [ ] Run in a test environment first
- [ ] Keep backups of important data
- [ ] Monitor API usage to detect unusual activity

### Maintenance
- [ ] Update to the latest version regularly
- [ ] Review and rotate API keys periodically
- [ ] Check for security advisories
- [ ] Report any suspicious behavior

## Security Roadmap

We are actively working on improving security:

- [ ] Code sandboxing/containerization
- [ ] Input validation and sanitization
- [ ] Rate limiting and abuse prevention
- [ ] Audit logging
- [ ] Code review before execution
- [ ] Resource limits for generated code
- [ ] Multi-factor authentication for API access

## Disclosure Policy

When a security vulnerability is confirmed:

1. We will develop and test a fix
2. We will release a security update
3. We will publish a security advisory
4. We will credit the reporter (if desired)
5. We will document the vulnerability in release notes

## Contact

For security concerns, contact:
- Email: devdattatalele@gmail.com
- GitHub: @devdattatalele

For general issues, use the GitHub issue tracker.

---

**Last Updated**: November 2024
