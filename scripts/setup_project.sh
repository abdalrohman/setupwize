#!/usr/bin/env bash

# --- Constants & Configuration ---
COLOR_RED=31
COLOR_GREEN=32
COLOR_YELLOW=33
COLOR_CYAN=36
DEFAULT_PY_VERSION="3.12"

# --- Functions ---

# Print colored messages
print_color() {
    local color_code="$1"
    local message="$2"
    echo -e "\033[${color_code}m${message}\033[0m"
}

# Display script usage/help
show_help() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help      Display this help message"
    echo "  -p, --python    Specify the Python version to install (default: ${DEFAULT_PY_VERSION})"
    echo "  -g, --git       Initialize a Git repository if one doesn't exist"
}

# Check if a command exists
command_exists() {
    command -v "$1" &>/dev/null
}

# Install pdm if not present
install_pdm() {
    if ! command_exists pdm; then
        print_color "${COLOR_YELLOW}" "pdm not installed. Installing now..."
        curl -sSL https://pdm-project.org/install-pdm.py | python3 - || {
            print_color "${COLOR_RED}" "pdm installation failed."
            exit 1
        }
    fi
}

# Initialize a Git repository
init_git() {
    if ! command_exists git || [ ! -d ".git" ]; then
        print_color "${COLOR_YELLOW}" "Initializing Git repository..."
        git init || {
            print_color "${COLOR_RED}" "Git initialization failed."
            exit 1
        }
    fi
}

# --- Main Script Logic ---

# Parse command-line options
while [[ $# -gt 0 ]]; do
    case "$1" in
    -h | --help)
        show_help
        exit 0
        ;;
    -p | --python)
        py_version="$2"
        shift 2
        ;;
    -g | --git)
        init_git_repo=true
        shift
        ;;
    *)
        echo "Invalid option: $1"
        show_help
        exit 1
        ;;
    esac
done

# Set default Python version if not specified
py_version="${py_version:-${DEFAULT_PY_VERSION}}"

# Install pdm
install_pdm

# Initialize Git repo if requested
if [[ "${init_git_repo}" == true ]]; then
    init_git
fi

# Install Python version
pdm python install "${py_version}"

# Initialize the project if pyproject.toml doesn't exist
if [ ! -f 'pyproject.toml' ]; then
    pdm init --python "${py_version}"
fi

# Set project Python version if needed
if [[ ! -d ".venv" ]] || [[ ! -f ".pdm-python" ]]; then
    pdm use "${py_version}"
fi

# Activate virtual environment
eval "$(pdm venv activate in-project)" || {
    print_color "${COLOR_RED}" "Error: Failed to activate virtual environment."
    exit 1
}

print_color "${COLOR_CYAN}" "WORKING VENV: ${VIRTUAL_ENV}"

# Install development dependencies
dev_packages=(
    "ipython"
    "ipykernel"
    "pre-commit"
    "virtualenv"
    "setuptools"
)
codespell="codespell"
lint="ruff"
typing="mypy"
dependencies=(
    "dotenv"
    "rich"
)

# Install dev packages
pdm add --group dev "${dev_packages[@]}"

# Install other groups
pdm add --group codespell --dev "${codespell}"
pdm add --group linting --dev "${lint}"
pdm add --group typing --dev "${typing}"

# Install main dependencies
pdm add "${dependencies[@]}"

# Install all dependencies
pdm install

# Install pre-commit hooks
if [[ "${init_git_repo}" == true ]]; then
    pdm run pre-commit install
fi

# Final instructions
print_color "${COLOR_GREEN}" "Setup complete."
print_color "${COLOR_GREEN}" "To activate the virtual environment, run:"
print_color "${COLOR_CYAN}" "eval \$(pdm venv activate in-project)"
