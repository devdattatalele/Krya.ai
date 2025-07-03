#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Creating icon files for Krya.ai...${NC}"

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}This script is designed for macOS. Please run on a Mac.${NC}"
    exit 1
fi

# Check for required tools
if ! command -v sips &> /dev/null || ! command -v iconutil &> /dev/null; then
    echo -e "${RED}Required tools (sips, iconutil) not found. These should be available on macOS.${NC}"
    exit 1
fi

# Create temporary directory
TEMP_DIR="./temp_iconset"
mkdir -p "$TEMP_DIR.iconset"

# Source image
SOURCE_IMAGE="./assests/krya_logo.png"
if [ ! -f "$SOURCE_IMAGE" ]; then
    echo -e "${RED}Source image not found: $SOURCE_IMAGE${NC}"
    exit 1
fi

# Generate different sizes
echo -e "${YELLOW}Generating different icon sizes...${NC}"
sips -z 16 16     "$SOURCE_IMAGE" --out "$TEMP_DIR.iconset/icon_16x16.png"
sips -z 32 32     "$SOURCE_IMAGE" --out "$TEMP_DIR.iconset/icon_16x16@2x.png"
sips -z 32 32     "$SOURCE_IMAGE" --out "$TEMP_DIR.iconset/icon_32x32.png"
sips -z 64 64     "$SOURCE_IMAGE" --out "$TEMP_DIR.iconset/icon_32x32@2x.png"
sips -z 128 128   "$SOURCE_IMAGE" --out "$TEMP_DIR.iconset/icon_128x128.png"
sips -z 256 256   "$SOURCE_IMAGE" --out "$TEMP_DIR.iconset/icon_128x128@2x.png"
sips -z 256 256   "$SOURCE_IMAGE" --out "$TEMP_DIR.iconset/icon_256x256.png"
sips -z 512 512   "$SOURCE_IMAGE" --out "$TEMP_DIR.iconset/icon_256x256@2x.png"
sips -z 512 512   "$SOURCE_IMAGE" --out "$TEMP_DIR.iconset/icon_512x512.png"
sips -z 1024 1024 "$SOURCE_IMAGE" --out "$TEMP_DIR.iconset/icon_512x512@2x.png"

# Convert to .icns file
echo -e "${YELLOW}Converting to .icns file...${NC}"
iconutil -c icns "$TEMP_DIR.iconset" -o "./assests/krya_logo.icns"

# Clean up
rm -rf "$TEMP_DIR.iconset"

echo -e "${GREEN}Icon files created successfully!${NC}"
echo -e "${YELLOW}Icon file location: ./assests/krya_logo.icns${NC}"

# Copy icon to Tauri icons directory
echo -e "${YELLOW}Copying icon to Tauri icons directory...${NC}"
cp "./assests/krya_logo.icns" "./ui/src-tauri/icons/icon.icns"

echo -e "${GREEN}Done!${NC}" 