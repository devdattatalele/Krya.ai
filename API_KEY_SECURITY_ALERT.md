# URGENT: API Key Security Alert

## ⚠️ CRITICAL SECURITY ISSUE DETECTED ⚠️

### Issue Description

A Google Gemini API key has been found in the repository at:
- `/src/config/config.json`

**Exposed API Key**: `AIzaSyCvEgjtJcfpJr0ihMA-erNFX-Awdpe6VWQ`

### Immediate Actions Required

#### For Repository Owners/Maintainers:

1. **REVOKE THE API KEY IMMEDIATELY**
   - Go to https://console.cloud.google.com/apis/credentials
   - Find the compromised API key
   - Click "Delete" or "Revoke"
   - Generate a new API key

2. **REMOVE FROM GIT HISTORY**
   ```bash
   # This file should never have been committed
   # Remove it from Git tracking
   git rm --cached src/config/config.json
   
   # Add to .gitignore (already done in this PR)
   echo "src/config/config.json" >> .gitignore
   echo "config/config.json" >> .gitignore
   
   # Commit the changes
   git commit -m "fix: Remove exposed API key and add to gitignore"
   ```

3. **ROTATE ALL SECRETS**
   - Generate new API keys
   - Update local `.env` files (not committed)
   - Notify any team members

4. **MONITOR FOR ABUSE**
   - Check Google Cloud Console for unusual API usage
   - Review billing for unexpected charges
   - Set up billing alerts

#### For Users Who Cloned the Repository:

1. **DO NOT USE THE EXPOSED KEY**
   - The key in `config.json` should be considered compromised
   - Get your own API key from https://aistudio.google.com/app/apikey

2. **SECURE YOUR OWN KEY**
   - Never commit your API key to Git
   - Use `.env` file (already in `.gitignore`)
   - Store keys in environment variables

3. **UPDATE YOUR LOCAL COPY**
   ```bash
   # Pull the latest changes
   git pull origin main
   
   # Ensure config.json is ignored
   git status  # config.json should not appear here
   
   # Create your own config
   cp config.json.example config.json
   # Edit config.json and add your own API key
   ```

### How This Happened

The `config.json` file containing the API key was committed to the repository, making it publicly accessible to anyone who cloned the repo.

### Prevention Measures Implemented

1. ✅ Added `config.json` to `.gitignore`
2. ✅ Created `config.json.example` as a template
3. ✅ Updated `.env.example` with clear instructions
4. ✅ Added security documentation (SECURITY.md)
5. ✅ Created setup guide emphasizing security

### Best Practices Going Forward

#### Never Commit These Files:
```
.env
config.json
*.key
*.pem
credentials.json
secrets.json
```

#### Always Use:
```
.env.example          (with placeholder values)
config.json.example   (with empty/default values)
```

#### Safe Configuration Workflow:

1. **Development:**
   ```bash
   # Copy example files
   cp .env.example .env
   cp config.json.example config.json
   
   # Add your real keys (these files are gitignored)
   nano .env  # Add real API key
   nano config.json  # Update with real key if needed
   ```

2. **Check Before Committing:**
   ```bash
   # Always verify what you're about to commit
   git status
   git diff
   
   # Make sure no sensitive files are staged
   # config.json should NOT appear in git status
   ```

3. **Environment Variables:**
   ```python
   # In code, always use environment variables
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   api_key = os.getenv("GOOGLE_API_KEY")
   
   # NEVER hardcode:
   # api_key = "AIzaSyC..."  # ❌ WRONG!
   ```

### Security Checklist for All Developers

Before every commit:
- [ ] Run `git status` to check what's being committed
- [ ] Run `git diff` to review changes
- [ ] Ensure no `.env` or `config.json` files are staged
- [ ] Verify API keys are not in any committed files
- [ ] Check that `.gitignore` is properly configured

### Tools to Help Prevent Secrets in Git

1. **git-secrets** (Amazon)
   ```bash
   # Install
   brew install git-secrets  # macOS
   
   # Set up
   git secrets --install
   git secrets --register-aws
   ```

2. **gitleaks** (Detect secrets in Git)
   ```bash
   # Install
   brew install gitleaks  # macOS
   
   # Scan repository
   gitleaks detect --source .
   ```

3. **pre-commit hooks**
   Create `.git/hooks/pre-commit`:
   ```bash
   #!/bin/bash
   
   # Check for potential secrets
   if git diff --cached | grep -i "AIza"; then
     echo "⚠️  Potential API key detected!"
     echo "Please remove before committing"
     exit 1
   fi
   ```

### Reporting Future Security Issues

If you discover exposed credentials:

1. **DO NOT** create a public issue
2. Email maintainer immediately: devdattatalele@gmail.com
3. Include:
   - Location of exposed credential
   - Type of credential (API key, password, etc.)
   - When it was committed (git log)

### Additional Resources

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [Google Cloud: Best practices for API keys](https://cloud.google.com/docs/authentication/api-keys#securing_an_api_key)
- [OWASP: Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

## Status

- [x] Issue identified
- [x] `.gitignore` updated
- [x] Example config files created
- [x] Security documentation added
- [ ] **PENDING**: Original API key must be revoked by repository owner
- [ ] **PENDING**: Remove from Git history (requires force push)

## Timeline

- **Discovered**: 2024-11-11
- **Documented**: 2024-11-11
- **Mitigation Started**: 2024-11-11
- **Full Resolution**: Pending maintainer action

---

**This is a serious security issue that requires immediate attention from repository maintainers.**
