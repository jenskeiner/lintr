"""Test configuration and fixtures."""

import os
import tempfile
from pathlib import Path
from typing import Any, Generator, Optional

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.monkeypatch import MonkeyPatch

from repolint.config import create_config_class


@pytest.fixture
def config_file() -> Generator[Optional[Path], None, None]:
    """Create a temporary configuration file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write("""
github_token: test-token
default_rule_set: test-ruleset
repository_filter:
  include_patterns:
    - "src/*"
    - "tests/*"
  exclude_patterns:
    - "**/temp/*"
rule_sets:
  basic:
    name: basic
    rules:
      - "has_readme"
""")
        f.flush()
        yield Path(f.name)
        os.unlink(f.name)


@pytest.fixture
def config(config_file: Path, monkeypatch: MonkeyPatch) -> Generator[Any, None, None]:
    """Create a configuration object."""
    # Set environment variables for testing
    monkeypatch.setenv("REPOLINT_GITHUB_TOKEN", "env-token")
    monkeypatch.setenv("REPOLINT_DEFAULT_RULE_SET", "env-ruleset")

    # Create config class with the temporary file
    RepolintConfig = create_config_class(yaml_file=config_file)
    yield RepolintConfig()
