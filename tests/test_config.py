"""Tests for the configuration module."""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Any

import pytest
from pydantic import ValidationError

from repolint.config import RepolintConfig, RepositoryFilter, RuleSetConfig


def test_repository_filter_defaults():
    """Test that RepositoryFilter has empty lists by default."""
    filter = RepositoryFilter()
    assert filter.include_patterns == []
    assert filter.exclude_patterns == []


def test_rule_set_config_validation():
    """Test that RuleSetConfig validates required fields."""
    # Name is required
    with pytest.raises(ValidationError):
        RuleSetConfig()

    # Rules and rule_sets are optional
    config = RuleSetConfig(name="test")
    assert config.rules == []
    assert config.rule_sets == []


def test_repolint_config_from_env():
    """Test loading configuration from environment variables."""
    os.environ["REPOLINT_GITHUB_TOKEN"] = "test-token"
    os.environ["REPOLINT_DEFAULT_RULE_SET"] = "custom-default"

    config = RepolintConfig()
    assert config.github_token == "test-token"
    assert config.default_rule_set == "custom-default"

    # Clean up
    del os.environ["REPOLINT_GITHUB_TOKEN"]
    del os.environ["REPOLINT_DEFAULT_RULE_SET"]


def test_repolint_config_defaults():
    """Test default values in RepolintConfig."""
    os.environ["REPOLINT_GITHUB_TOKEN"] = "test-token"
    config = RepolintConfig()

    assert config.github_token == "test-token"
    assert config.default_rule_set == "default"
    assert config.repository_filter is None
    assert config.repository_rule_sets == {}
    assert config.rule_sets == {}

    # Clean up
    del os.environ["REPOLINT_GITHUB_TOKEN"]


def test_repolint_config_from_yaml():
    """Test loading configuration from YAML file."""
    yaml_content = """
    github_token: test-token
    default_rule_set: custom-default
    repository_filter:
      include_patterns:
        - "python-*"
      exclude_patterns:
        - "*-archived"
    repository_rule_sets:
      my-repo: python-lib
    rule_sets:
      python-lib:
        name: python-lib
        rules:
          - R001
          - R002
        rule_sets:
          - base
    """

    with NamedTemporaryFile(mode="w", suffix=".yaml") as f:
        f.write(yaml_content)
        f.flush()

        config = RepolintConfig.from_yaml(f.name)

    assert config.github_token == "test-token"
    assert config.default_rule_set == "custom-default"
    assert config.repository_filter is not None
    assert config.repository_filter.include_patterns == ["python-*"]
    assert config.repository_filter.exclude_patterns == ["*-archived"]
    assert config.repository_rule_sets == {"my-repo": "python-lib"}
    assert "python-lib" in config.rule_sets
    assert config.rule_sets["python-lib"].rules == ["R001", "R002"]
    assert config.rule_sets["python-lib"].rule_sets == ["base"]


def test_repolint_config_from_yaml_file_not_found():
    """Test error when YAML file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        RepolintConfig.from_yaml("nonexistent.yaml")
