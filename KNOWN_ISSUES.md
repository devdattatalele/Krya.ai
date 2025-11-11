# Known Issues and User Problems

This document identifies potential issues and problems users may encounter while using Krya.ai, along with recommended solutions and improvements.

## Critical Security Issues

### 1. **API Key Exposure in Repository** 🔴 CRITICAL
**Problem:** The file `/src/config/config.json` contains a hardcoded Google Gemini API key (`AIzaSyCvEgjtJcfpJr0ihMA-erNFX-Awdpe6VWQ`) which is committed to the repository.

**Impact:** 
- Anyone with repository access can use this API key
- Potential for API quota exhaustion
- Unauthorized usage and charges
- Security breach

**Solution:**
- Immediately revoke the exposed API key
- Add `config.json` to `.gitignore`
- Use environment variables exclusively for API keys
- Never commit API keys to version control

### 2. **Inadequate Security Policy**
**Problem:** `SECURITY.md` contains placeholder text with fake version numbers (5.1.x, 5.0.x, 4.0.x) that don't match the actual project version (0.1.0).

**Impact:**
- Confusing for users reporting vulnerabilities
- No clear security contact or process
- Unprofessional appearance

**Solution:**
- Update SECURITY.md with actual project versions
- Add clear vulnerability reporting process
- Include security contact information

## Installation and Setup Issues

### 3. **Inconsistent Installation Instructions**
**Problem:** README.md and BUILD_INSTRUCTIONS.md provide different setup approaches:
- README mentions Streamlit (old approach)
- BUILD_INSTRUCTIONS mentions Tauri + FastAPI (new approach)
- No clear migration guide

**Impact:**
- User confusion about which method to use
- Wasted time following outdated instructions
- Failed installations

**Solution:**
- Update README to reflect current architecture
- Archive or remove outdated Streamlit instructions
- Add clear "Getting Started" section

### 4. **Missing Prerequisites Validation**
**Problem:** No automated check for Python version, required libraries, or system requirements before installation.

**Impact:**
- Runtime errors during execution
- Cryptic error messages
- Difficult troubleshooting

**Solution:**
- Add requirements checker script
- Validate Python version (3.8+)
- Check for system-specific dependencies (especially for PyAutoGUI)

### 5. **Platform-Specific Issues Not Documented**
**Problem:** PyAutoGUI requires additional setup on different platforms:
- macOS requires Accessibility permissions
- Linux requires X server dependencies
- Windows may need admin privileges

**Impact:**
- Application fails to control mouse/keyboard
- Cryptic permission errors
- Users abandon the project

**Solution:**
- Add platform-specific setup instructions
- Document required permissions
- Provide troubleshooting for common permission issues

## Dependency and Version Issues

### 6. **Outdated or Vulnerable Dependencies**
**Problem:** Several dependencies may have security vulnerabilities:
- `google.generativeai>=0.3.0` (very old version, current is 0.8.x+)
- No dependency lock files (`requirements.txt` uses `>=` instead of `==`)
- No automated security scanning

**Impact:**
- Security vulnerabilities
- Compatibility issues
- Unpredictable behavior across installations

**Solution:**
- Update to latest stable versions
- Use lock files (requirements.txt with exact versions)
- Add dependency scanning (Dependabot, Snyk)
- Pin versions for reproducibility

### 7. **Missing Python Virtual Environment Guide**
**Problem:** No instructions to use virtual environments for Python dependencies.

**Impact:**
- Global Python environment pollution
- Version conflicts with other projects
- Difficult to reproduce issues

**Solution:**
- Add venv/virtualenv setup instructions
- Recommend using pipenv or poetry
- Update documentation with best practices

## Configuration Issues

### 8. **No Configuration Validation**
**Problem:** Application doesn't validate configuration before running:
- Invalid API keys silently fail
- Malformed JSON in config.json causes crashes
- No feedback on configuration errors

**Impact:**
- Cryptic runtime errors
- Difficult debugging
- Poor user experience

**Solution:**
- Add config validation on startup
- Provide clear error messages
- Add config file schema validation

### 9. **Environment Variables Not Well Documented**
**Problem:** `.env.example` only shows `GOOGLE_API_KEY` but code references other potential config options.

**Impact:**
- Users don't know what configuration options exist
- Trial and error configuration
- Suboptimal usage

**Solution:**
- Complete `.env.example` with all options
- Add comments explaining each variable
- Document environment variable hierarchy

## Runtime and Execution Issues

### 10. **Uncontrolled Code Execution**
**Problem:** The application generates and executes arbitrary Python code without sandboxing:
- Generated code runs with full system privileges
- No resource limits (CPU, memory, disk)
- Can potentially harm the system

**Impact:**
- Security risk from malicious or buggy generated code
- System crashes or hangs
- Data loss potential

**Solution:**
- Implement code sandboxing
- Add resource limits
- Provide execution previews before running
- Add safety checks for dangerous operations

### 11. **No Process Timeout Management**
**Problem:** Generated scripts can run indefinitely without timeout controls visible to user.

**Impact:**
- Hung processes
- Resource exhaustion
- Poor user experience

**Solution:**
- Add configurable timeout settings
- Show timeout warnings
- Allow users to adjust timeouts per task

### 12. **Poor Error Handling and Feedback**
**Problem:** Error messages are not user-friendly:
- Stack traces shown directly to users
- No suggestions for common errors
- Limited retry mechanisms

**Impact:**
- Users don't understand what went wrong
- Difficult to diagnose issues
- High support burden

**Solution:**
- Wrap technical errors in user-friendly messages
- Add error code system
- Provide actionable suggestions
- Improve logging

## UI/UX Issues

### 13. **No Progress Indicators for Long Operations**
**Problem:** No clear feedback during code generation and execution phases.

**Impact:**
- Users don't know if app is working or frozen
- Premature cancellation of operations
- Poor user experience

**Solution:**
- Add progress bars
- Show status messages
- Provide estimated completion times

### 14. **Limited Input Validation**
**Problem:** User prompts are not validated before processing:
- Empty prompts accepted
- No length limits
- Special characters not handled

**Impact:**
- Wasted API calls
- Unexpected errors
- Poor user experience

**Solution:**
- Add prompt validation
- Set reasonable length limits
- Sanitize inputs

### 15. **No Execution History Persistence**
**Problem:** Execution history only stored in session state, lost on restart.

**Impact:**
- Lost history of what was executed
- Cannot review past results
- Difficult to debug issues

**Solution:**
- Persist execution history to database/file
- Add history viewing feature
- Allow users to re-run past prompts

## Documentation Issues

### 16. **Incomplete API Documentation**
**Problem:** FastAPI endpoints are not fully documented:
- No examples for API usage
- Missing request/response schemas in docs
- No API versioning

**Impact:**
- Difficult to integrate with other tools
- Trial and error API usage
- Breaking changes without notice

**Solution:**
- Complete OpenAPI documentation
- Add usage examples
- Implement API versioning

### 17. **No Troubleshooting Guide**
**Problem:** README lacks troubleshooting section for common issues.

**Impact:**
- Users stuck on common problems
- High support requests
- User abandonment

**Solution:**
- Add TROUBLESHOOTING.md
- Document common errors and solutions
- Include FAQ section

### 18. **Missing Contributing Guidelines**
**Problem:** No CONTRIBUTING.md with guidelines for contributors.

**Impact:**
- Inconsistent contributions
- Unclear process for PRs
- Low contribution quality

**Solution:**
- Add CONTRIBUTING.md
- Define code style guidelines
- Document PR process

## Performance Issues

### 19. **No Rate Limiting on API Calls**
**Problem:** Application can make unlimited API calls rapidly.

**Impact:**
- API quota exhaustion
- Unexpected costs
- Service degradation

**Solution:**
- Implement rate limiting
- Add quota tracking
- Warn users about API usage

### 20. **Memory Leaks in Long-Running Sessions**
**Problem:** Application state grows unbounded (recent_logs, active_processes).

**Impact:**
- Memory exhaustion over time
- Application slowdown
- Crashes in long sessions

**Solution:**
- Implement proper cleanup
- Add memory limits
- Periodically clear old data

## Testing Issues

### 21. **No Test Suite**
**Problem:** Despite `pytest>=7.4.3` in requirements, no tests exist in the repository.

**Impact:**
- No confidence in code changes
- Easy to introduce bugs
- Difficult to maintain

**Solution:**
- Add unit tests
- Add integration tests
- Set up CI/CD pipeline

### 22. **No Continuous Integration**
**Problem:** No CI/CD pipeline to automatically test changes.

**Impact:**
- Breaking changes go unnoticed
- No automated quality checks
- Manual testing burden

**Solution:**
- Add GitHub Actions workflows
- Automate testing and linting
- Add security scanning

## Architecture Issues

### 23. **Tight Coupling Between Components**
**Problem:** Frontend, backend, and business logic are tightly coupled.

**Impact:**
- Difficult to test
- Hard to maintain
- Cannot easily swap components

**Solution:**
- Implement dependency injection
- Define clear interfaces
- Separate concerns

### 24. **No Database for Persistent Storage**
**Problem:** All data stored in memory or files.

**Impact:**
- Data loss on restart
- No multi-user support
- Limited scalability

**Solution:**
- Add database (SQLite for simple use)
- Implement proper data models
- Add migration system

## Licensing and Legal Issues

### 25. **Unclear Model Usage Rights**
**Problem:** No documentation about rights and limitations when using generated code.

**Impact:**
- Legal uncertainty
- Potential copyright issues
- Commercial use concerns

**Solution:**
- Document code ownership
- Clarify usage rights
- Add disclaimer

## Accessibility Issues

### 26. **No Keyboard Shortcuts for UI**
**Problem:** All interactions require mouse clicks.

**Impact:**
- Poor accessibility
- Slower workflow
- Limited usability

**Solution:**
- Add keyboard shortcuts
- Document shortcuts
- Follow accessibility guidelines

### 27. **No Dark Mode Support**
**Problem:** UI only supports light mode.

**Impact:**
- Eye strain
- Poor user experience in dark environments
- No user preference options

**Solution:**
- Add dark mode toggle
- Respect system preferences
- Persist user choice

## Priority Recommendations

### Immediate (Fix Now)
1. ✅ Revoke and remove exposed API key
2. ✅ Add config.json to .gitignore
3. ✅ Update security policy
4. ✅ Add platform-specific setup instructions

### Short Term (This Week)
5. ✅ Update dependencies to latest versions
6. ✅ Add input validation
7. ✅ Improve error messages
8. ✅ Add troubleshooting guide

### Medium Term (This Month)
9. ✅ Add test suite
10. ✅ Implement rate limiting
11. ✅ Add code sandboxing
12. ✅ Set up CI/CD

### Long Term (This Quarter)
13. ✅ Refactor architecture
14. ✅ Add database support
15. ✅ Implement proper authentication
16. ✅ Build plugin system
