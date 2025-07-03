# Building Krya.AI Application

This document provides instructions for building the Krya.AI application for different platforms.

## Prerequisites

Before building, make sure you have the following tools installed:

- **Python 3.x**
- **Node.js and npm**
- **Rust and Cargo** (for Tauri)
- On macOS, you'll need **create-dmg** for creating DMG installers (will be installed automatically)

## Building the Application

### Step 1: Generate Icon Files (macOS only)

If you're on macOS and want to create a proper .icns file for the application:

```bash
cd /path/to/Krya.ai
./create_icons.sh
```

This will create the necessary icon files for macOS.

### Step 2: Build the Application

To build the application for your current platform:

```bash
cd /path/to/Krya.ai
./build.sh
```

The build script will:
1. Check for required dependencies
2. Build the FastAPI backend
3. Build the Tauri frontend
4. Package everything together
5. Create platform-specific installers (DMG for macOS, MSI for Windows, AppImage/DEB for Linux)

### Step 3: Install and Run

#### macOS
- Open the `dist/Krya.ai.dmg` file
- Drag the Krya.app to your Applications folder
- Run Krya.app from your Applications folder

#### Windows
- Run the MSI installer in `dist/windows/`
- Launch Krya.ai from the Start Menu

#### Linux
- Use the AppImage in `dist/linux/` or install the DEB package

## Manual Running

If you prefer to run the application manually:

```bash
# Start the backend
cd /path/to/Krya.ai/src
python run_server.py

# In another terminal, start the frontend
cd /path/to/Krya.ai/ui
npm run tauri dev
```

## Keyboard Shortcut

The application can be activated using:
- **Cmd+K** on macOS
- **Ctrl+K** on Windows/Linux

## Troubleshooting

If you encounter any issues:

1. Make sure all prerequisites are installed
2. Check that the API server is running on port 8000
3. Verify that there are no other applications using the same keyboard shortcut

For more detailed help, please refer to the main README.md file or open an issue on the GitHub repository. 