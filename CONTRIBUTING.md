# Contributing to SetUpWize

Thank you for your interest in contributing to SetUpWize! This document provides guidelines and instructions for contributing to the project.

## Development Environment Setup

### Using uv (Recommended)

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

# Install development dependencies
uv pip install -e ".[dev,linting,typing,codespell]"

# Install pre-commit hooks
pre-commit install
```

## Code Style

We use [Ruff](https://github.com/astral-sh/ruff) for code formatting and linting. The configuration is in `ruff.toml`.

- Use 4 spaces for indentation
- Maximum line length is 120 characters
- Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for docstrings
- Use type hints for all function parameters and return values

## Testing

We use [pytest](https://docs.pytest.org/) for testing. All tests are in the `tests` directory.

- Write unit tests for all new functionality
- Ensure all tests pass before submitting a pull request
- Aim for high test coverage

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=setupwize

# Run specific tests
pytest tests/unit/core/test_package.py
```

## Pull Request Process

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Run tests and ensure they pass
5. Run linting and formatting checks
6. Submit a pull request

## Adding New Features

### Adding a New Task Type

1. Add a new executor class in `src/setupwize/core/task.py`
2. Update the `create_task_from_config` function to handle the new task type
3. Add tests for the new task type

### Adding a New Package

1. Create a new YAML file in the `packages` directory
2. Follow the package configuration format
3. Test the package installation

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT license.
