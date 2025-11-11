# Complete Setup Guide

This comprehensive guide will walk you through setting up Krya.ai on your system.

## Table of Contents
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Detailed Installation](#detailed-installation)
- [Platform-Specific Setup](#platform-specific-setup)
- [Configuration](#configuration)
- [Verification](#verification)
- [Common Issues](#common-issues)

---

## System Requirements

### Minimum Requirements
- **OS**: macOS 10.15+, Windows 10+, or Linux (Ubuntu 20.04+)
- **RAM**: 4 GB
- **Disk Space**: 2 GB free
- **Internet**: Required for API calls

### Required Software
- Python 3.8 or higher
- Node.js 16+ and npm (for UI)
- Rust and Cargo (for Tauri builds)
- Git

### Optional but Recommended
- Visual Studio Code or PyCharm
- Virtual environment tool (venv, virtualenv, or conda)
- Terminal emulator with good Unicode support

---

## Quick Start

For experienced developers who want to get started quickly:

```bash
# 1. Clone repository
git clone https://github.com/devdattatalele/Krya.ai.git
cd Krya.ai

# 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r src/requirements.txt

# 3. Configure API key
cp .env.example .env
# Edit .env and add: GOOGLE_API_KEY=your_key_here

# 4. Run backend
cd src
python run_server.py

# 5. (Optional) Run UI in another terminal
cd ui
npm install
npm run tauri dev
```

---

## Detailed Installation

### Step 1: Install Python

#### macOS
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Verify installation
python3 --version
```

#### Windows
1. Download Python from https://www.python.org/downloads/
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Choose "Install Now"
5. Verify in Command Prompt:
   ```cmd
   python --version
   ```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
python3 --version
```

### Step 2: Install Node.js and npm

#### macOS
```bash
brew install node
node --version
npm --version
```

#### Windows
1. Download from https://nodejs.org/
2. Run installer (choose LTS version)
3. Verify in Command Prompt:
   ```cmd
   node --version
   npm --version
   ```

#### Linux
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version
npm --version
```

### Step 3: Install Rust (for Tauri)

All platforms:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Follow prompts, then:
```bash
source $HOME/.cargo/env  # On Linux/macOS
# On Windows, restart your terminal
rustc --version
cargo --version
```

### Step 4: Clone Repository

```bash
git clone https://github.com/devdattatalele/Krya.ai.git
cd Krya.ai
```

### Step 5: Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows (Command Prompt):
venv\Scripts\activate.bat

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# You should see (venv) in your prompt
```

### Step 6: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r src/requirements.txt
```

**If you encounter errors**, install packages individually:
```bash
pip install fastapi uvicorn python-dotenv
pip install google-generativeai pyautogui pydantic
pip install websockets psutil pytest httpx python-multipart
```

### Step 7: Install UI Dependencies (Optional)

```bash
cd ui
npm install
cd ..
```

---

## Platform-Specific Setup

### macOS Additional Setup

#### 1. Grant Accessibility Permissions

Krya.ai needs to control your mouse and keyboard:

1. Open **System Preferences** → **Security & Privacy** → **Privacy** → **Accessibility**
2. Click the lock icon 🔒 and authenticate
3. Click **+** and add your Terminal app (or iTerm2, etc.)
4. Restart your terminal

#### 2. Grant Screen Recording Permission (if needed)

1. **System Preferences** → **Security & Privacy** → **Privacy** → **Screen Recording**
2. Add your Terminal app
3. Restart your terminal

#### 3. Install Additional Tools

```bash
# For DMG creation (if building from source)
npm install -g create-dmg
```

### Windows Additional Setup

#### 1. Enable Script Execution

Open PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. Install Visual C++ Redistributable

Download and install from:
https://aka.ms/vs/17/release/vc_redist.x64.exe

#### 3. Windows Defender Exclusions (Optional)

To prevent false positives:
1. **Windows Security** → **Virus & threat protection** → **Manage settings**
2. Scroll to **Exclusions** → **Add or remove exclusions**
3. Add the Krya.ai folder

### Linux Additional Setup

#### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-tk \
    python3-dev \
    scrot \
    libxcb-randr0-dev \
    libxcb-xtest0-dev \
    libxcb-xinerama0-dev \
    libxcb-shape0-dev \
    libxcb-xkb-dev
```

**Fedora/RHEL:**
```bash
sudo dnf install -y \
    python3-tkinter \
    python3-devel \
    scrot \
    libxcb-devel
```

#### 2. X11 vs Wayland

PyAutoGUI works best on X11. If using Wayland:
1. Log out
2. At login screen, click the gear icon ⚙️
3. Select "Ubuntu on Xorg" or similar X11 session
4. Log back in

---

## Configuration

### Step 1: Get Google Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click **Create API Key**
4. Select or create a project
5. Copy the generated key (starts with `AIza...`)
6. Store it securely (you'll need it in the next step)

### Step 2: Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env file and add your API key
# On macOS/Linux:
nano .env

# On Windows:
notepad .env
```

Add this line to `.env`:
```
GOOGLE_API_KEY=AIzaSyC...your_actual_key_here...
```

⚠️ **Important**: Never commit this file to Git! It's already in `.gitignore`.

### Step 3: Configure Application Settings (Optional)

```bash
# Copy example configuration
cp config.json.example config.json

# Edit if needed (optional)
nano config.json  # or notepad config.json on Windows
```

Default `config.json`:
```json
{
  "api_key": "",
  "model_name": "gemini-2.5-flash",
  "temperature": 1.55,
  "max_output_tokens": 8192,
  "top_p": 0.95,
  "top_k": 40
}
```

Configuration options:
- `model_name`: Gemini model to use (`gemini-2.5-flash` or `gemini-2.5-pro`)
- `temperature`: Creativity level (0.0-2.0, higher = more creative)
- `max_output_tokens`: Maximum length of generated code
- `top_p`, `top_k`: Sampling parameters

---

## Verification

### Test Backend Setup

```bash
cd src
python run_server.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

In another terminal, test the API:
```bash
curl http://localhost:8000
```

Expected response:
```json
{"status":"online","service":"Krya.ai API"}
```

### Test API Key

```bash
curl -X POST http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{"api_key":"YOUR_API_KEY"}'
```

### Test UI (Optional)

If you installed UI dependencies:

```bash
cd ui
npm run tauri dev
```

The application window should open.

### Run a Simple Test

1. Start the backend: `python src/run_server.py`
2. Open another terminal
3. Try a simple automation:
   ```bash
   curl -X POST http://localhost:8000/run \
     -H "Content-Type: application/json" \
     -d '{"prompt":"Open Notepad and type Hello World","max_retries":3}'
   ```

---

## Common Issues

### "python3: command not found"

**Solution**: Install Python (see Step 1)

### "pip: command not found"

**Solution**:
```bash
python3 -m ensurepip --upgrade
```

### "Permission denied" when running scripts

**Solution**:
```bash
chmod +x build.sh create_icons.sh
```

### Port 8000 already in use

**Solution**:
```bash
# Find and kill the process
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
# Note the PID, then:
taskkill /PID <PID> /F
```

### PyAutoGUI not working

**Solution**: Check platform-specific setup above, especially permissions.

### "Module not found" errors

**Solution**: Ensure virtual environment is activated:
```bash
# Check if (venv) appears in prompt
# If not, activate again:
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate.bat  # Windows
```

---

## Next Steps

After successful setup:

1. ✅ Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
2. ✅ Review [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for limitations
3. ✅ Check [SECURITY.md](SECURITY.md) for security best practices
4. ✅ Try the sample prompts in the UI
5. ✅ Join discussions on GitHub

---

## Getting Help

If you're still stuck:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Search [GitHub Issues](https://github.com/devdattatalele/Krya.ai/issues)
3. Create a new issue with:
   - Your OS and version
   - Python version
   - Complete error message
   - What you've tried

---

**Congratulations! You're ready to use Krya.ai! 🎉**
