#!/usr/bin/env bash

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Building padam-cli binary..."

# Ensure uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: 'uv' is required but not installed.${NC}"
    exit 1
fi

# Sync dependencies and build using PyInstaller via uv run
uv sync
echo "Running PyInstaller..."
uv run pyinstaller --onefile --name padam-cli main.py

# Define install directory
INSTALL_DIR="$HOME/.local/bin"

# Move the compiled binary
echo "Installing to $INSTALL_DIR..."
cp dist/padam-cli "$INSTALL_DIR/padam-cli"
chmod +x "$INSTALL_DIR/padam-cli"

# Check PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${RED}Warning: $INSTALL_DIR is not in your PATH.${NC}"
    echo "Add 'export PATH=\"$INSTALL_DIR:\$PATH\"' to your ~/.bashrc or ~/.zshrc"
fi

echo -e "${GREEN}Installation complete! You can now run 'padam-cli'.${NC}"