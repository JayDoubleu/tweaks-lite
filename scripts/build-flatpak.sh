#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Build directories
BUILD_DIR="/tmp/tweaks-lite-build"
STATE_DIR="/tmp/tweaks-lite-state"
REPO_DIR="/tmp/tweaks-lite-repo"

# Clean up existing directories
echo -e "${GREEN}Cleaning up previous build directories...${NC}"
rm -rf $BUILD_DIR $STATE_DIR $REPO_DIR

# Build and install Flatpak
echo -e "${GREEN}Building and installing Flatpak...${NC}"
flatpak-builder \
    --user \
    --install \
    --force-clean \
    --state-dir=$STATE_DIR \
    --repo=$REPO_DIR \
    $BUILD_DIR \
    dev.jaydoubleu.tweaks.lite.json

# Check if build was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Flatpak build and installation successful!${NC}"
else
    echo -e "${RED}Flatpak build failed!${NC}"
    exit 1
fi
