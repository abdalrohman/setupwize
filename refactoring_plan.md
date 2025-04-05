# SetUpWize Refactoring Plan

## 1. Project Structure Reorganization

Current structure is somewhat flat. We'll reorganize to:

```
setupwize/
├── src/
│   └── setupwize/
│       ├── __init__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── environment.py  (renamed from env.py)
│       │   ├── exceptions.py
│       │   ├── package.py      (renamed from packages.py)
│       │   ├── selector.py     (renamed from interactive_selector.py)
│       │   ├── shell.py        (renamed from run_cmd.py)
│       │   └── task.py         (renamed from tasks.py)
│       ├── parsers/
│       │   ├── __init__.py
│       │   └── yaml_parser.py
│       ├── tracers/
│       │   ├── __init__.py
│       │   └── log.py
│       └── utils/
│           ├── __init__.py
│           └── system.py       (renamed from utils.py)
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── test_environment.py
│   │   │   ├── test_package.py
│   │   │   ├── test_selector.py
│   │   │   ├── test_shell.py
│   │   │   └── test_task.py
│   │   ├── parsers/
│   │   │   ├── __init__.py
│   │   │   └── test_yaml_parser.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── test_system.py
│   └── integration/
│       ├── __init__.py
│       └── test_cli.py
├── configurations/  (unchanged)
├── packages/        (unchanged)
├── pyproject.toml   (updated)
├── README.md        (updated)
└── .env             (unchanged)
```

## 2. Dependency Management

- Replace PDM with uv for package management
- Update dependencies to latest versions:
  - click -> 8.1.7+
  - python-dotenv -> 1.0.1+
  - questionary -> 2.0.1+
  - rich -> 13.9.4+
  - Replace tdqm with tqdm 4.66.2+
- Add proper development dependencies:
  - pytest 7.4.0+
  - pytest-cov 4.1.0+
  - mypy 1.13.0+
  - ruff 0.8.3+

## 3. Code Refactoring

### 3.1 Replace Inheritance with Composition

- Refactor `Task` class hierarchy to use composition
- Create task factories instead of inheritance-based task creation

### 3.2 Improve Type Hinting

- Add proper type hints throughout the codebase
- Use Python 3.11+ type features (TypedDict, Unpack, etc.)
- Add type checking with mypy

### 3.3 Enhance Error Handling

- Implement proper exception handling
- Add context managers for resource management
- Use more specific exceptions

### 3.4 Implement Proper Logging

- Refactor logging to use structured logging
- Improve log message clarity and consistency

### 3.5 Improve Code Organization and Modularity

- Split large functions into smaller, more focused ones
- Use dataclasses for data structures
- Implement proper dependency injection

## 4. Testing

- Add unit tests for core functionality
- Implement test fixtures
- Add test coverage reporting
- Add integration tests for CLI

## 5. Documentation

- Add proper docstrings (Google style)
- Update README.md with usage examples
- Add CONTRIBUTING.md with development guidelines
