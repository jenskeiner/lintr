# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Lintr is a Python-based command-line tool for linting and enforcing consistent settings across GitHub repositories. It helps maintain repository hygiene by checking configurations against predefined rules and can automatically fix common issues.

## Common Commands

### Development Setup
```bash
# Install dependencies using uv
uv install --dev

# Run tests
pytest

# Run tests with coverage
pytest --cov=lintr --cov-report=term-missing --cov-report=html

# Run a single test file
pytest tests/test_cli.py

# Run specific test
pytest tests/test_cli.py::test_handle_lint
```

### CLI Usage
```bash
# Initialize a new configuration file
lintr init

# Run linter on repositories
lintr lint

# Run with auto-fix enabled
lintr lint --fix

# Run in dry-run mode
lintr lint --dry-run

# List available rules
lintr list --rules

# List available rule sets
lintr list --rule-sets
```

### Package Management
```bash
# Install package in development mode
uv pip install -e .

# Build package
python -m build

# Install from source
pip install .
```

## Architecture Overview

### Core Components

1. **CLI Layer** (`cli.py`): Command-line interface with argparse handling for `lint`, `list`, `init`, and `help` commands
2. **Configuration** (`config.py`): Pydantic-based configuration management with support for YAML files and environment variables
3. **GitHub Integration** (`gh.py`): GitHub API client using PyGithub for repository access
4. **Linter Engine** (`linter.py`): Core linting logic that orchestrates rule execution and result reporting
5. **Rule System** (`rules/`): Extensible rule framework with base classes and specific rule implementations

### Rule System Architecture

The rule system is built around several key concepts:

- **Rule Base Class** (`rules/base.py`): Abstract base class defining the rule interface with `check()` and `fix()` methods
- **Rule Categories**: Rules are organized into categories (General, Branches, GitFlow, etc.)
- **Rule Manager** (`rule_manager.py`): Singleton that discovers and manages rules via entry points
- **Rule Sets** (`rules/base.py`): Collections of rules that can be composed and reused
- **Rule Context** (`rules/context.py`): Provides context information to rules during execution

### Entry Points System

Rules and rule sets are discovered via setuptools entry points:
- `lintr.rules`: Individual rule classes
- `lintr.rule_sets`: Rule set factory functions

### Configuration System

Configuration is handled through:
1. YAML configuration files (default: `lintr.yml`)
2. Environment variables (prefixed with `LINTR_`)
3. `.env` files for development
4. Pydantic models for validation and type safety

## Key Design Patterns

### Plugin Architecture
Rules are loaded dynamically via entry points, allowing for easy extension without modifying core code.

### Singleton Pattern
The RuleManager uses a singleton pattern to ensure consistent rule discovery and management across the application.

### Command Pattern
Each CLI command has a dedicated handler function that encapsulates the command logic.

### Factory Pattern
Rule sets are created via factory functions rather than direct instantiation.

## Testing Strategy

- **pytest** for test framework
- **Coverage reporting** with pytest-cov
- **Fixtures** for common test objects (repositories, configurations, rule managers)
- **Mock objects** for GitHub API interactions
- **Isolated test environment** with clean environment variables per test

## Configuration Files

### Primary Configuration (`lintr.yml`)
- Repository filtering patterns
- Rule set definitions
- Repository-specific configurations
- GitHub token configuration

### Development Configuration (`pyproject.toml`)
- Package metadata and dependencies
- Entry points for rules and rule sets
- Test configuration
- Build system configuration

## Rule Development

### Creating New Rules
1. Inherit from `Rule[ConfigT]` base class
2. Define required class attributes (`_id`, `_description`, `_category`)
3. Implement `check()` method returning `RuleCheckResult`
4. Optionally implement `fix()` method for automatic remediation
5. Register via entry points in `pyproject.toml`

### Rule Categories
- **General (G)**: Repository settings and features
- **Branches (B)**: Branch-related rules
- **GitFlow (GF)**: Git-flow specific rules
- **Rules (R)**: Branch protection and rulesets
- **Miscellaneous (M)**: Other rules

## Error Handling

- Configuration validation via Pydantic
- Graceful handling of GitHub API errors
- Rule execution errors are caught and reported
- Comprehensive error messages for troubleshooting

## Dependencies

### Core Runtime
- `PyGithub`: GitHub API integration
- `pydantic`: Configuration validation
- `PyYAML`: YAML configuration parsing
- `rich`: Rich text and colored console output

### Development
- `pytest`: Testing framework
- `pytest-cov`: Coverage reporting
- `pre-commit`: Git hooks for code quality

## Special Notes

- Uses custom PyGithub fork with rules and rulesets support
- Requires Python 3.12+
- GitHub token required for API access
- Supports both personal and organization repositories
- Dry-run mode available for safe testing