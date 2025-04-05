#!/bin/bash

# Run tests for SetUpWize

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

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_color "${BLUE}" "Activating virtual environment..."
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        print_color "${RED}" "Virtual environment not found. Please run ./install.sh first."
        exit 1
    fi
fi

# Run tests
print_color "${BLUE}" "Running tests..."
python -m pytest

print_color "${GREEN}" "Tests completed!"
