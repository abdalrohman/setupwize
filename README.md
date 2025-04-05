# SetUpWize

Your friendly tool installation wizard!

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Overview

SetUpWize is a Python-based tool that helps you set up your development environment by installing and configuring various tools and packages. It uses YAML configuration files to define packages and their installation tasks.

## Features

- Install packages from YAML configuration files
- Interactive package selection
- Support for different desktop environments (GNOME, KDE Neon)
- Logging and error handling
- Modular design for easy extension

## Installation

### Using the install script (Recommended)

The easiest way to install SetUpWize is to use the provided install script:

```bash
# Clone the repository
git clone https://github.com/yourusername/setupwize.git
cd setupwize

# Run the install script
./install.sh
```

This script will:
1. Install uv if it's not already installed
2. Create a virtual environment
3. Install the package in development mode

### Manual installation with uv

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver. To install SetUpWize manually using uv:

```bash
# Install uv if you don't have it
curl -sSf https://astral.sh/uv/install.sh | bash

# Clone the repository
git clone https://github.com/yourusername/setupwize.git
cd setupwize

# Create a virtual environment and install the package
uv venv
source .venv/bin/activate
uv pip install -e .

# Install development dependencies (optional)
uv pip install -e ".[dev,linting,typing,codespell]"
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/setupwize.git
cd setupwize

# Create a virtual environment and install the package
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Install development dependencies (optional)
pip install -e ".[dev,linting,typing,codespell]"
```

## Usage

```bash
# List available packages
setupwize --list-packages

# Install specific packages
setupwize package1 package2

# Interactively select packages to install
setupwize --select-packages

# Enable verbose output
setupwize --verbose package1 package2

# Specify custom packages directory
setupwize --packages-dir /path/to/packages package1 package2

# Specify custom log level and path
setupwize --log-level DEBUG --log-path /path/to/logs package1 package2
```

## Package Configuration

Packages are defined in YAML files in the `packages` directory. Each package file should follow this format:

```yaml
packages:
  - name: package_name
    description: Package description
    category: Category
    tasks:
      - type: apt
        action: install
        packages:
          - package1
          - package2
      - type: shell
        command: |
          echo "Hello, world!"
      - type: configuration
        config_path:
          - ./configurations/config_file
        destination:
          - ~/.config/destination
    dependencies:
      - dependency1
      - dependency2
```

## Development

### Running Tests

The easiest way to run tests is to use the provided script:

```bash
# Run all tests
./run_tests.sh
```

This script will activate the virtual environment if needed and run all tests.

You can also run tests manually:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=setupwize

# Run specific tests
pytest tests/unit/core/test_package.py
```

### Code Formatting and Linting

The project includes a Makefile with commands for formatting and linting:

```bash
# Format code
make format

# Lint code
make lint

# Spell checking
make spell_check

# Clean up cache files
make clean
```

You can also run these commands manually:

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking
uv run mypy .

# Spell checking
uv run codespell
```

## License

MIT
