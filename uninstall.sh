#!/usr/bin/env bash

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

BINARY_NAME="padam-cli"
INSTALL_DIR="$HOME/.local/bin"
TARGET_PATH="$INSTALL_DIR/$BINARY_NAME"

echo "Starting uninstallation of $BINARY_NAME..."

# Check if the binary exists before trying to delete it
if [ -f "$TARGET_PATH" ]; then
    echo "Removing binary from $INSTALL_DIR..."
    rm "$TARGET_PATH"
    echo -e "${GREEN}Successfully removed $BINARY_NAME binary.${NC}"
else
    echo -e "${YELLOW}Warning: $BINARY_NAME was not found in $INSTALL_DIR.${NC}"
fi

# Clean up local repository build files if they exist
if [ -d "dist" ] || [ -d "build" ]; then
    echo "Cleaning up local build and dist directories..."
    rm -rf dist build *.spec
fi

# Remind the user about their shell configuration file
echo -e "\n${YELLOW}Note:${NC} If you added '$INSTALL_DIR' to your PATH manually in your shell profile,"
echo "you may want to remove it from your ~/.bashrc or ~/.zshrc if it is no longer needed."

echo -e "\n${GREEN}Uninstallation complete!${NC}"
