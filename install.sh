#!/bin/bash

# Install script for SetUpWize using uv

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print colored message
print_color() {
    echo -e "${1}${2}${NC}"
}

# Check if uv is installed
if ! command -v uv &>/dev/null; then
    print_color "${BLUE}" "Installing uv..."
    curl -sSf https://astral.sh/uv/install.sh | bash

    # Add uv to PATH for this session
    export PATH="$HOME/.cargo/bin:$PATH"
fi

print_color "${GREEN}" "uv is installed!"

# Create virtual environment
print_color "${BLUE}" "Creating virtual environment..."
uv venv

# Activate virtual environment
print_color "${BLUE}" "Activating virtual environment..."
source .venv/bin/activate

# Install package
print_color "${BLUE}" "Installing SetUpWize..."
uv pip install -e .

print_color "${GREEN}" "Installation complete!"
print_color "${GREEN}" "You can now use SetUpWize by running 'setupwize' command."
print_color "${GREEN}" "To activate the virtual environment in the future, run:"
print_color "${BLUE}" "source .venv/bin/activate"
