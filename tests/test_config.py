"""Tests for configuration handling."""

import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from repolint.config import RepositoryFilter, RuleSetConfig, create_config_class


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env") as f:
        f.write("REPOLINT_GITHUB_TOKEN=env-file-token\n")
        f.write("REPOLINT_DEFAULT_RULE_SET=env-file-ruleset\n")
        f.flush()
        yield Path(f.name)


@pytest.fixture
def temp_yaml_file():
    """Create a temporary YAML config file."""
    yaml_content = """
github_token: yaml-token
default_rule_set: yaml-ruleset
repository_filter:
  include_patterns:
    - src/*
    - tests/*
  exclude_patterns:
    - "**/temp/*"
rule_sets:
  basic:
    name: basic
    rules:
      - has_readme
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml") as f:
        f.write(yaml_content)
        f.flush()
        yield Path(f.name)


def test_repository_filter_defaults():
    """Test default values for RepositoryFilter."""
    filter_config = RepositoryFilter()
    assert filter_config.include_patterns == []
    assert filter_config.exclude_patterns == []


def test_rule_set_config_validation():
    """Test validation of RuleSetConfig."""
    # Test required fields
    with pytest.raises(ValidationError):
        RuleSetConfig()

    # Test with only required fields
    config = RuleSetConfig(name="test")
    assert config.name == "test"
    assert config.rules == []
    assert config.rule_sets == []


def test_config_source_priority(temp_env_file, temp_yaml_file, monkeypatch):
    """Test that configuration sources are applied in the correct priority order.

    Priority (highest to lowest):
    1. Environment variables
    2. .env file
    3. YAML config file
    """
    # Set up environment variables
    monkeypatch.setenv("REPOLINT_GITHUB_TOKEN", "env-var-token")
    monkeypatch.setenv("REPOLINT_DEFAULT_RULE_SET", "env-var-ruleset")

    # Test with all sources
    RepolintConfig = create_config_class(yaml_file=temp_yaml_file)
    config = RepolintConfig()

    # Environment variables should take precedence
    assert config.github_token == "env-var-token"
    assert config.default_rule_set == "env-var-ruleset"


def test_config_source_fallback(temp_yaml_file):
    """Test that configuration falls back to lower priority sources when higher ones don't define values."""
    # Only use YAML file (no env vars or .env)
    RepolintConfig = create_config_class(yaml_file=temp_yaml_file)
    config = RepolintConfig(github_token="test-token")  # Required field

    # Should use values from YAML
    assert config.github_token == "test-token"
    assert config.default_rule_set == "yaml-ruleset"


def test_config_partial_override(temp_yaml_file, monkeypatch):
    """Test that partial configuration in higher priority sources only overrides those specific values."""
    # Set only one env var
    monkeypatch.setenv("REPOLINT_GITHUB_TOKEN", "env-var-token")

    RepolintConfig = create_config_class(yaml_file=temp_yaml_file)
    config = RepolintConfig()

    # Should use env var for token but YAML for ruleset
    assert config.github_token == "env-var-token"
    assert config.default_rule_set == "yaml-ruleset"


def test_config_without_yaml(monkeypatch):
    """Test configuration without a YAML file."""
    monkeypatch.setenv("REPOLINT_GITHUB_TOKEN", "env-var-token")
    monkeypatch.setenv("REPOLINT_DEFAULT_RULE_SET", "env-var-ruleset")

    RepolintConfig = create_config_class()  # No config file
    config = RepolintConfig()

    assert config.github_token == "env-var-token"
    assert config.default_rule_set == "env-var-ruleset"


def test_config_complex_types(temp_yaml_file, monkeypatch):
    """Test handling of complex types (lists, dicts) from different sources."""
    monkeypatch.setenv("REPOLINT_GITHUB_TOKEN", "env-var-token")
    monkeypatch.setenv("REPOLINT_REPOSITORY_FILTER__INCLUDE_PATTERNS", '["env/*"]')

    RepolintConfig = create_config_class(yaml_file=temp_yaml_file)
    config = RepolintConfig()

    # Environment variables should override YAML values
    assert config.repository_filter.include_patterns == ["env/*"]
    assert config.repository_filter.exclude_patterns == ["**/temp/*"]


def test_config_invalid_yaml(monkeypatch):
    """Test handling of invalid YAML configuration."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml") as f:
        f.write("invalid: yaml: file:")  # Invalid YAML
        f.flush()

        # Should still load from env vars even if YAML is invalid
        monkeypatch.setenv("REPOLINT_GITHUB_TOKEN", "env-var-token")

        with pytest.raises(ValidationError):
            RepolintConfig = create_config_class(yaml_file=Path(f.name))
            RepolintConfig()


def test_config_missing_required():
    """Test error when required fields are missing."""
    RepolintConfig = create_config_class()
    with pytest.raises(ValidationError):
        RepolintConfig()


def test_repolint_config_from_env(monkeypatch):
    """Test loading configuration from environment variables."""
    # Override environment with specific values
    monkeypatch.setenv("REPOLINT_GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("REPOLINT_DEFAULT_RULE_SET", "custom-default")

    RepolintConfig = create_config_class()
    config = RepolintConfig()

    assert config.github_token == "test-token"
    assert config.default_rule_set == "custom-default"


def test_repolint_config_defaults():
    """Test default values in RepolintConfig."""
    RepolintConfig = create_config_class()
    config = RepolintConfig(github_token="test-token")

    assert config.default_rule_set == "empty"  # Default value
    assert isinstance(config.repository_filter, RepositoryFilter)
    assert config.repository_filter.include_patterns == []
    assert config.repository_filter.exclude_patterns == []
    assert config.rule_sets == {}


def test_repolint_config_from_yaml():
    """Test loading configuration from YAML file."""
    yaml_content = """
github_token: test-token
default_rule_set: custom-default
repository_filter:
  include_patterns:
    - python-*
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

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as f:
        f.write(yaml_content)
        f.flush()

        RepolintConfig = create_config_class(yaml_file=Path(f.name))
        config = RepolintConfig()

        assert config.github_token == "test-token"
        assert config.default_rule_set == "custom-default"
        assert config.repository_filter.include_patterns == ["python-*"]
        assert config.repository_filter.exclude_patterns == ["*-archived"]
        assert config.repository_rule_sets == {"my-repo": "python-lib"}
        assert "python-lib" in config.rule_sets
        assert config.rule_sets["python-lib"].name == "python-lib"
        assert config.rule_sets["python-lib"].rules == ["R001", "R002"]
        assert config.rule_sets["python-lib"].rule_sets == ["base"]


def test_repolint_config_yaml_file_not_found():
    """Test error when YAML file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        create_config_class(yaml_file=Path("nonexistent.yaml"))
