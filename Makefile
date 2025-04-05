# Variables
PYTHON_FILES := src tests
MYPY_CACHE := .mypy_cache
RUFF_CACHE := .ruff_cache

# Targets
.PHONY: all format lint spell_check spell_fix clean help test coverage install

all: help

lint: ## Run linters
	@echo "\033[33mLinting...\033[0m"
	@uv run ruff check .
	uv run ruff format $(PYTHON_FILES) --diff
	uv run ruff check --select I $(PYTHON_FILES)
	mkdir -p $(MYPY_CACHE) && uv run mypy $(PYTHON_FILES) --cache-dir $(MYPY_CACHE)

format: ## Run code formatters
	@echo "\033[34mFormatting...\033[0m"
	uv run ruff format $(PYTHON_FILES)
	uv run ruff check --select I --fix $(PYTHON_FILES)

spell_check: ## Run codespell on the project
	@echo "\033[35mSpell checking...\033[0m"
	uv run codespell --toml pyproject.toml

spell_fix: ## Run codespell on the project and fix the errors
	@echo "\033[35mSpell fixing...\033[0m"
	uv run codespell --toml pyproject.toml -w

test: ## Run tests
	@echo "\033[32mRunning tests...\033[0m"
	uv run pytest

coverage: ## Run tests with coverage
	@echo "\033[32mRunning tests with coverage...\033[0m"
	uv run pytest --cov=setupwize --cov-report=html
	echo "Coverage report is available in htmlcov/index.html"

install: ## Install the package
	@echo "\033[32mInstalling the package...\033[0m"
	uv pip install -e .

install-dev: ## Install the package with development dependencies
	@echo "\033[32mInstalling the package with development dependencies...\033[0m"
	uv pip install -e ".[dev,linting,typing,codespell]"

clean: ## Clean up the project
	@echo "\033[31mCleaning...\033[0m"
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "$(MYPY_CACHE)" -exec rm -r {} +
	find . -type d -name "$(RUFF_CACHE)" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf htmlcov
	rm -rf .coverage

help: ## Show this help message
	@echo "\033[36mAvailable targets:\033[0m"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
