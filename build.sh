#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Krya.ai build process...${NC}"

# Check for required tools
echo -e "${YELLOW}Checking for required tools...${NC}"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.${NC}"
    exit 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js.${NC}"
    exit 1
fi

# Check for npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is not installed. Please install npm.${NC}"
    exit 1
fi

# Check for Rust/Cargo (required for Tauri)
if ! command -v cargo &> /dev/null; then
    echo -e "${RED}Rust/Cargo is not installed. Please install Rust (https://rustup.rs/).${NC}"
    exit 1
fi

# Check for create-dmg on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v create-dmg &> /dev/null; then
        echo -e "${YELLOW}create-dmg is not installed. Installing it now...${NC}"
        npm install -g create-dmg || {
            echo -e "${RED}Failed to install create-dmg. Please install it manually: npm install -g create-dmg${NC}"
            exit 1
        }
    fi
fi

echo -e "${GREEN}All required tools are installed.${NC}"

# Create build directory
BUILD_DIR="./dist"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

# Build FastAPI backend
echo -e "${YELLOW}Building FastAPI backend...${NC}"
cd src
pip3 install -r requirements.txt
cd ..

# Copy backend files to build directory
echo -e "${YELLOW}Copying backend files...${NC}"
mkdir -p $BUILD_DIR/api
cp -r src/* $BUILD_DIR/api/
cp -r .env $BUILD_DIR/api/ 2>/dev/null || :  # Copy .env if exists

# Ensure the resources directory exists in the Tauri app
echo -e "${YELLOW}Preparing resources directory...${NC}"
mkdir -p ui/src-tauri/resources
cp -r src ui/src-tauri/resources/

# Build Tauri frontend
echo -e "${YELLOW}Building Tauri frontend...${NC}"
cd ui
npm install
npm run tauri build
cd ..

# Copy Tauri build to dist
echo -e "${YELLOW}Copying Tauri build...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - check both possible paths
    if [ -d "ui/src-tauri/target/release/bundle/macos/Krya.ai.app" ]; then
        cp -r ui/src-tauri/target/release/bundle/macos/Krya.ai.app $BUILD_DIR/
    elif [ -d "ui/src-tauri/target/release/bundle/macos/Krya.app" ]; then
        cp -r ui/src-tauri/target/release/bundle/macos/Krya.app $BUILD_DIR/
    else
        echo -e "${RED}Could not find Tauri app bundle. Checking alternative locations...${NC}"
        find ui/src-tauri/target -name "*.app" -type d
        
        # Try to use the DMG that was created directly
        if [ -f "ui/src-tauri/target/release/bundle/dmg/Krya.ai_0.1.0_aarch64.dmg" ]; then
            echo -e "${YELLOW}Found DMG file created by Tauri. Copying it directly...${NC}"
            cp ui/src-tauri/target/release/bundle/dmg/Krya.ai_0.1.0_aarch64.dmg $BUILD_DIR/Krya.ai.dmg
            echo -e "${GREEN}DMG installer copied to: $BUILD_DIR/Krya.ai.dmg${NC}"
            echo -e "${YELLOW}To install, open the DMG file and drag the app to your Applications folder.${NC}"
            exit 0
        else
            echo -e "${RED}No app bundle or DMG found. Build failed.${NC}"
            exit 1
        fi
    fi
    
    # Check for icon file
    ICON_FILE="assests/krya_logo.icns"
    if [ ! -f "$ICON_FILE" ]; then
        echo -e "${YELLOW}Icon file not found. Using default icon.${NC}"
        ICON_FILE="ui/src-tauri/icons/icon.icns"
    fi
    
    # Create DMG file
    echo -e "${YELLOW}Creating DMG file...${NC}"
    APP_NAME=$(find $BUILD_DIR -name "*.app" -type d -maxdepth 1 | head -1 | xargs basename)
    
    if [ -z "$APP_NAME" ]; then
        echo -e "${RED}Could not find app bundle in $BUILD_DIR. DMG creation failed.${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Using app bundle: $APP_NAME${NC}"
    
    create-dmg \
        --volname "Krya.ai" \
        --volicon "$ICON_FILE" \
        --window-pos 200 120 \
        --window-size 800 400 \
        --icon-size 100 \
        --icon "$APP_NAME" 200 190 \
        --hide-extension "$APP_NAME" \
        --app-drop-link 600 185 \
        --no-internet-enable \
        "$BUILD_DIR/Krya.ai.dmg" \
        "$BUILD_DIR/$APP_NAME" || {
            echo -e "${YELLOW}DMG creation with create-dmg failed. Trying hdiutil...${NC}"
            
            # Alternative method using hdiutil
            TMP_DMG="$BUILD_DIR/tmp.dmg"
            FINAL_DMG="$BUILD_DIR/Krya.ai.dmg"
            
            # Create a temporary DMG
            hdiutil create -volname "Krya.ai" -srcfolder "$BUILD_DIR/$APP_NAME" -ov -format UDRW "$TMP_DMG"
            
            # Convert the temporary DMG to the final DMG
            hdiutil convert "$TMP_DMG" -format UDZO -o "$FINAL_DMG"
            
            # Clean up
            rm -f "$TMP_DMG"
            
            if [ -f "$FINAL_DMG" ]; then
                echo -e "${GREEN}DMG created successfully using hdiutil.${NC}"
            else
                echo -e "${RED}Failed to create DMG. You can still use the app bundle at $BUILD_DIR/$APP_NAME${NC}"
            fi
        }
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    mkdir -p $BUILD_DIR/linux
    cp -r ui/src-tauri/target/release/bundle/appimage/* $BUILD_DIR/linux/
    cp -r ui/src-tauri/target/release/bundle/deb/* $BUILD_DIR/linux/
elif [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    mkdir -p $BUILD_DIR/windows
    cp -r ui/src-tauri/target/release/bundle/msi/* $BUILD_DIR/windows/
else
    echo -e "${RED}Unsupported OS: $OSTYPE${NC}"
    exit 1
fi

# Create startup script
echo -e "${YELLOW}Creating startup script...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    cat > $BUILD_DIR/start_krya.sh << 'EOF'
#!/bin/bash
# Start the API server
cd "$(dirname "$0")/api"
python3 run_server.py --port 8000 &
API_PID=$!

# Wait for API server to start
sleep 2

# Start the Tauri app
open ../Krya.app

# Function to handle exit
function cleanup {
  echo "Shutting down API server..."
  kill $API_PID
  exit 0
}

# Register the cleanup function for exit signals
trap cleanup SIGINT SIGTERM

# Keep script running to maintain API server
echo "Krya.ai is running. Press Ctrl+C to exit."
wait $API_PID
EOF
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    cat > $BUILD_DIR/start_krya.sh << 'EOF'
#!/bin/bash
# Start the API server
cd "$(dirname "$0")/api"
python3 run_server.py --port 8000 &
API_PID=$!

# Wait for API server to start
sleep 2

# Start the Tauri app
../linux/krya.AppImage &
APP_PID=$!

# Function to handle exit
function cleanup {
  echo "Shutting down Krya.ai..."
  kill $API_PID
  kill $APP_PID
  exit 0
}

# Register the cleanup function for exit signals
trap cleanup SIGINT SIGTERM

# Keep script running to maintain API server
echo "Krya.ai is running. Press Ctrl+C to exit."
wait $API_PID
EOF
elif [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    cat > $BUILD_DIR/start_krya.bat << 'EOF'
@echo off
REM Start the API server
cd api
start python run_server.py --port 8000

REM Wait for API server to start
timeout /t 2

REM Start the Tauri app
cd ..
start windows\Krya.exe

echo Krya.ai is running. Close this window to exit.
pause
taskkill /f /im python.exe
EOF
fi

# Make startup script executable
if [[ "$OSTYPE" != "msys"* ]] && [[ "$OSTYPE" != "win32" ]]; then
    chmod +x $BUILD_DIR/start_krya.sh
fi

echo -e "${GREEN}Build completed successfully!${NC}"
echo -e "${YELLOW}To start Krya.ai, run:${NC}"
if [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo -e "${GREEN}  dist\\start_krya.bat${NC}"
else
    echo -e "${GREEN}  ./dist/start_krya.sh${NC}"
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${GREEN}DMG installer created at: $BUILD_DIR/Krya.ai.dmg${NC}"
    echo -e "${YELLOW}To install, open the DMG file and drag the app to your Applications folder.${NC}"
fi 