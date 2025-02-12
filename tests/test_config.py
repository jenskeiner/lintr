"""Tests for configuration handling."""

import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from repolint.config import RepositoryFilter, RuleSetConfig, create_config_class


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


def test_source_priority(env, env_file, config_file, monkeypatch):
    """Test that configuration sources are applied in the correct priority order.

    Priority (highest to lowest):
    1. Environment variables
    2. .env file
    3. YAML config file
    """
    # Create config with all sources
    RepolintConfig = create_config_class(yaml_file=config_file.path)
    config = RepolintConfig()

    # 1. Environment variables should take precedence over both .env and yaml
    assert config.github_token == "env-var-token"
    assert config.default_rule_set == "env-var-ruleset"

    # 2. Remove env vars to test .env file precedence over yaml
    monkeypatch.delenv("REPOLINT_GITHUB_TOKEN")
    monkeypatch.delenv("REPOLINT_DEFAULT_RULE_SET")
    config = RepolintConfig()
    assert config.github_token == "env-file-token"
    assert config.default_rule_set == "env-file-ruleset"

    # 3. Test yaml-only values (not set in env or .env)
    assert config.repository_filter.include_patterns == ["src/*", "tests/*"]
    assert config.repository_filter.exclude_patterns == ["**/temp/*"]
    assert config.rule_sets["basic"].name == "basic"
    assert config.rule_sets["basic"].rules == ["has_readme"]


def test_missing_config_file():
    """Test error when YAML file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        create_config_class(yaml_file=Path("nonexistent.yaml"))


def test_invalid_config_file(monkeypatch):
    """Test handling of invalid YAML configuration."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml") as f:
        f.write("invalid: yaml: file:")  # Invalid YAML
        f.flush()

        with pytest.raises(ValidationError):
            RepolintConfig = create_config_class(yaml_file=Path(f.name))
            RepolintConfig()


def test_missing_required_fields():
    """Test error when required fields are missing."""
    RepolintConfig = create_config_class()
    with pytest.raises(ValidationError):
        RepolintConfig()


def test_defaults():
    """Test default values in RepolintConfig."""
    RepolintConfig = create_config_class()
    config = RepolintConfig(github_token="test-token")

    assert config.default_rule_set == "empty"  # Default value
    assert isinstance(config.repository_filter, RepositoryFilter)
    assert config.repository_filter.include_patterns == []
    assert config.repository_filter.exclude_patterns == []
    assert config.rule_sets == {}
