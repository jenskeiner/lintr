# Repolint

A Python-based command-line application to lint and enforce consistent settings across GitHub repositories.

## Features

- Lint repositories to check for specific conditions based on defined rules
- Support for configuration files to specify target repositories and custom rule-sets
- Pre-defined rule-sets for common project types
- Both linting and autofix capabilities
- Extensible through custom rules

## Development

This project uses `uv` for build and packaging. To get started:

1. Install uv (if not already installed)
2. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Unix-like systems
   uv pip install -e ".[dev]"
   ```

3. Run tests:
   ```bash
   pytest
   ```

## License

MIT License
