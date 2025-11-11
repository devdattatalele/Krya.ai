# Troubleshooting Guide

This guide helps you resolve common issues when using Krya.ai.

## Table of Contents
- [Installation Issues](#installation-issues)
- [API and Authentication Issues](#api-and-authentication-issues)
- [Execution Issues](#execution-issues)
- [Permission Issues](#permission-issues)
- [Performance Issues](#performance-issues)
- [UI Issues](#ui-issues)
- [Platform-Specific Issues](#platform-specific-issues)

---

## Installation Issues

### Python Dependencies Not Installing

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions:**
1. Ensure Python 3.8 or higher is installed:
   ```bash
   python3 --version
   ```

2. Upgrade pip:
   ```bash
   pip install --upgrade pip
   ```

3. Install dependencies one by one to identify the problematic package:
   ```bash
   pip install pyautogui
   pip install google-generativeai
   # ... etc
   ```

4. Use a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r src/requirements.txt
   ```

### Node.js/npm Errors

**Symptoms:**
```
npm ERR! code ENOENT
```

**Solutions:**
1. Check Node.js installation:
   ```bash
   node --version
   npm --version
   ```

2. Clear npm cache:
   ```bash
   npm cache clean --force
   ```

3. Delete node_modules and reinstall:
   ```bash
   cd ui
   rm -rf node_modules package-lock.json
   npm install
   ```

### Rust/Cargo Not Found (Tauri Build)

**Symptoms:**
```
error: cargo not found
```

**Solutions:**
1. Install Rust from https://rustup.rs/:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. Restart your terminal after installation

3. Verify installation:
   ```bash
   cargo --version
   ```

---

## API and Authentication Issues

### "API key not configured" Error

**Symptoms:**
- Application won't start
- Error message about missing API key

**Solutions:**
1. Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

2. Add your Gemini API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

3. Get an API key from https://aistudio.google.com/app/apikey

4. Restart the application after adding the key

### "Invalid API key" or "401 Unauthorized" Error

**Symptoms:**
```
Error: 401 Unauthorized
```

**Solutions:**
1. Verify your API key is correct (check for extra spaces)

2. Ensure the API key has not expired or been revoked

3. Check that you've enabled the Gemini API in Google Cloud Console

4. Try generating a new API key

### API Rate Limit Exceeded

**Symptoms:**
```
Error: 429 Too Many Requests
```

**Solutions:**
1. Wait a few minutes before retrying

2. Check your API quota in Google Cloud Console

3. Upgrade your API plan if needed

4. Implement delays between requests in your code

---

## Execution Issues

### Generated Code Fails to Execute

**Symptoms:**
- Code generates but doesn't run
- "Execution failed" messages
- No visible effects

**Solutions:**
1. Check the execution logs for specific errors

2. Verify PyAutoGUI has necessary permissions (see Permission Issues)

3. Try a simpler prompt first:
   ```
   "Open Notepad and type 'Hello World'"
   ```

4. Check if the application you're trying to control is installed and accessible

5. Ensure no other application is blocking the mouse/keyboard

### Code Execution Timeout

**Symptoms:**
```
Execution timed out after 60 seconds
```

**Solutions:**
1. Increase timeout in settings (if using UI)

2. Simplify your prompt to require less time

3. Break complex tasks into smaller steps

4. Check if the generated code has infinite loops

### Script Hangs or Freezes

**Symptoms:**
- Application becomes unresponsive
- CPU usage at 100%
- Must force quit

**Solutions:**
1. Use the Stop button in the UI

2. Kill the process manually:
   ```bash
   # On macOS/Linux
   pkill -f "generated_output.py"
   
   # On Windows
   taskkill /F /IM python.exe
   ```

3. Restart the application

4. Check the generated code for issues before execution

---

## Permission Issues

### macOS: "Accessibility Permissions Required"

**Symptoms:**
```
Error: Accessibility permissions not granted
```

**Solutions:**
1. Open System Preferences → Security & Privacy → Privacy → Accessibility

2. Click the lock icon and enter your password

3. Find Terminal (or your terminal app) and check the box

4. If using the Tauri app, add "Krya.ai" to the list

5. Restart the application

### macOS: "Screen Recording Permission Required"

**Symptoms:**
- Screenshots fail
- Cannot detect screen elements

**Solutions:**
1. Open System Preferences → Security & Privacy → Privacy → Screen Recording

2. Add your terminal or Krya.ai app to the list

3. Restart the application

### Linux: X11 Display Issues

**Symptoms:**
```
Error: Could not open display
```

**Solutions:**
1. Ensure X server is running:
   ```bash
   echo $DISPLAY
   ```

2. Install required packages:
   ```bash
   sudo apt-get install python3-tk python3-dev
   sudo apt-get install xdotool  # Alternative automation tool
   ```

3. If using WSL, install VcXsrv or X410

### Windows: Admin Privileges Required

**Symptoms:**
- Cannot control certain applications
- Permission denied errors

**Solutions:**
1. Run the application as Administrator (right-click → Run as administrator)

2. Disable UAC prompts for development (not recommended for production)

3. Use Windows-specific automation alternatives

---

## Performance Issues

### High CPU Usage

**Symptoms:**
- Computer becomes slow
- Fan noise increases
- Battery drains quickly

**Solutions:**
1. Reduce `max_retries` setting

2. Increase delays in generated code

3. Close unnecessary applications

4. Monitor process in Task Manager/Activity Monitor

5. Limit concurrent executions

### High Memory Usage

**Symptoms:**
- Application uses several GB of RAM
- System swapping to disk
- Out of memory errors

**Solutions:**
1. Restart the application regularly

2. Clear execution history

3. Reduce log retention

4. Check for memory leaks in generated code

5. Use smaller model for code generation

### Slow Response Times

**Symptoms:**
- Long wait for code generation
- Delayed execution

**Solutions:**
1. Check internet connection (API calls require internet)

2. Try a different Gemini model:
   - `gemini-2.5-flash` (faster, less capable)
   - `gemini-2.5-pro` (slower, more capable)

3. Reduce `max_output_tokens` in config

4. Clear browser cache if using web UI

---

## UI Issues

### Streamlit UI Won't Start

**Symptoms:**
```
command not found: streamlit
```

**Solutions:**
1. Install Streamlit:
   ```bash
   pip install streamlit
   ```

2. Run from correct directory:
   ```bash
   cd src
   streamlit run main.py
   ```

3. Check port 8501 is not in use:
   ```bash
   lsof -ti:8501  # On macOS/Linux
   netstat -ano | findstr :8501  # On Windows
   ```

### Tauri UI Won't Start

**Symptoms:**
- Blank window
- Error messages in console

**Solutions:**
1. Ensure backend is running:
   ```bash
   cd src
   python run_server.py
   ```

2. Check backend is accessible:
   ```bash
   curl http://localhost:8000
   ```

3. Rebuild the UI:
   ```bash
   cd ui
   npm run build
   npm run tauri dev
   ```

4. Check console for JavaScript errors

### UI Elements Not Responding

**Symptoms:**
- Buttons don't work
- Input fields frozen

**Solutions:**
1. Refresh the page (if web UI)

2. Restart the application

3. Clear browser cache and cookies

4. Check browser console for errors

5. Try a different browser

---

## Platform-Specific Issues

### macOS: "App is damaged and can't be opened"

**Symptoms:**
- Cannot open installed app
- Gatekeeper blocking

**Solutions:**
1. Remove quarantine attribute:
   ```bash
   xattr -cr /Applications/Krya.ai.app
   ```

2. Allow in System Preferences → Security & Privacy

3. Build from source instead of using pre-built binary

### macOS: Keyboard Shortcut Not Working (Cmd+K)

**Symptoms:**
- Cmd+K doesn't activate app
- Other app captures the shortcut

**Solutions:**
1. Close conflicting applications

2. Change the keyboard shortcut in settings

3. Check System Preferences → Keyboard → Shortcuts for conflicts

### Windows: Antivirus Blocking Execution

**Symptoms:**
- Generated scripts deleted immediately
- "Virus detected" warnings

**Solutions:**
1. Add Krya.ai folder to antivirus exclusions

2. Use Windows Defender exclusions:
   - Windows Security → Virus & threat protection → Exclusions

3. Create exception for Python processes

### Linux: PyAutoGUI Not Working on Wayland

**Symptoms:**
```
Error: PyAutoGUI not supported on Wayland
```

**Solutions:**
1. Switch to X11 session (log out and select at login screen)

2. Or install and use alternative tools:
   ```bash
   sudo apt-get install python3-xlib
   pip install pynput  # Alternative to PyAutoGUI
   ```

3. Use `xdotool` for basic automation

---

## Common Error Messages

### "No module named 'google.generativeai'"

**Solution:**
```bash
pip install google-generativeai
```

### "ImportError: DLL load failed" (Windows)

**Solution:**
Install Microsoft Visual C++ Redistributable from:
https://aka.ms/vs/17/release/vc_redist.x64.exe

### "ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]"

**Solution:**
```bash
# macOS
/Applications/Python\ 3.x/Install\ Certificates.command

# Or upgrade certificates
pip install --upgrade certifi
```

### "Port 8000 already in use"

**Solution:**
```bash
# Find and kill process using port 8000
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## Getting Help

If you've tried these solutions and still have issues:

1. **Check GitHub Issues**: Search for similar problems at https://github.com/devdattatalele/Krya.ai/issues

2. **Create a New Issue**: Include:
   - Operating system and version
   - Python version
   - Complete error message
   - Steps to reproduce
   - What you've already tried

3. **Enable Debug Logging**: Set log level to DEBUG in code for more details

4. **Community Support**: Join discussions in the repository

---

## Preventive Measures

### Before Running
- ✅ Check all prerequisites are installed
- ✅ Verify API key is configured
- ✅ Ensure sufficient disk space
- ✅ Close sensitive applications
- ✅ Save your work in other applications

### Regular Maintenance
- 🔄 Update dependencies monthly
- 🔄 Clear old logs and temporary files
- 🔄 Restart application after heavy use
- 🔄 Back up configuration files
- 🔄 Monitor API usage and costs

### Security Best Practices
- 🔒 Never commit API keys to git
- 🔒 Review generated code before execution
- 🔒 Don't run in production environments
- 🔒 Limit access to sensitive files/folders
- 🔒 Keep backups of important data
