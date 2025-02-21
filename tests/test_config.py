"""Tests for configuration handling."""

import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from lintr.config import (
    RepositoryFilter,
    RuleSetConfig,
    RepositoryConfig,
    create_config_class,
)


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
    config = RuleSetConfig(description="test")
    assert config.description == "test"
    assert config.rules == []


def test_source_priority(env, env_file, config_file, monkeypatch):
    """Test that configuration sources are applied in the correct priority order.

    Priority (highest to lowest):
    1. Environment variables
    2. .env file
    3. YAML config file
    """
    # Create config with all sources
    LintrConfig = create_config_class(yaml_file=config_file.path)
    config = LintrConfig()

    # 1. Environment variables should take precedence over both .env and yaml
    assert config.github_token == "env-var-token"
    assert config.default_ruleset == "env-var-ruleset"

    # 2. Remove env vars to test .env file precedence over yaml
    monkeypatch.delenv("LINTR_GITHUB_TOKEN")
    monkeypatch.delenv("LINTR_DEFAULT_RULESET")
    config = LintrConfig()
    assert config.github_token == "env-file-token"
    assert config.default_ruleset == "env-file-ruleset"

    # 3. Test yaml-only values (not set in env or .env)
    assert config.repository_filter.include_patterns == ["src/*", "tests/*"]
    assert config.repository_filter.exclude_patterns == ["**/temp/*"]
    assert config.rulesets["basic"].description == "basic"
    assert config.rulesets["basic"].rules == ["R001"]


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
            LintrConfig = create_config_class(yaml_file=Path(f.name))
            LintrConfig()


def test_missing_required_fields():
    """Test error when required fields are missing."""
    LintrConfig = create_config_class()
    with pytest.raises(ValidationError):
        LintrConfig()


def test_defaults():
    """Test default values in LintrConfig."""
    LintrConfig = create_config_class()
    config = LintrConfig(github_token="test-token")

    assert config.default_ruleset == "empty"  # Default value
    assert isinstance(config.repository_filter, RepositoryFilter)
    assert config.repository_filter.include_patterns == []
    assert config.repository_filter.exclude_patterns == []
    assert config.rulesets == {}


def test_custom_rule_definition():
    """Test defining custom rules by inheriting from existing rules."""
    LintrConfig = create_config_class()
    config = LintrConfig(
        github_token="test-token",
        rules={
            "custom_readme": {
                "base": "has_readme",
                "description": "Custom readme rule",
                "config": {"required_sections": ["Installation", "Usage"]},
            }
        },
    )

    assert "custom_readme" in config.rules
    custom_rule = config.rules["custom_readme"]
    assert custom_rule.base == "has_readme"
    assert custom_rule.description == "Custom readme rule"
    assert custom_rule.config == {"required_sections": ["Installation", "Usage"]}


def test_custom_rule_validation():
    """Test validation of custom rule definitions."""
    LintrConfig = create_config_class()

    # Test missing required fields
    with pytest.raises(ValidationError):
        LintrConfig(
            github_token="test-token",
            rules={"invalid_rule": {"description": "Missing base rule"}},
        )

    # Test invalid base rule format
    with pytest.raises(ValidationError):
        LintrConfig(
            github_token="test-token",
            rules={
                "invalid_rule": {
                    "base": 123,  # Should be string
                    "description": "Invalid base rule type",
                    "config": {},
                }
            },
        )


def test_repository_specific_rule_config():
    """Test overriding rule configuration at repository level."""
    LintrConfig = create_config_class()
    config = LintrConfig(
        github_token="test-token",
        rules={
            "custom_readme": {
                "base": "has_readme",
                "description": "Custom readme rule",
                "config": {"required_sections": ["Installation", "Usage"]},
            }
        },
        repositories={
            "owner/repo": RepositoryConfig(
                ruleset="custom",
                rules={
                    "custom_readme": {
                        "required_sections": ["Quick Start"]  # Override default config
                    }
                },
            )
        },
    )

    repo_config = config.repositories["owner/repo"]
    assert repo_config.rules["custom_readme"]["required_sections"] == ["Quick Start"]


def test_multiple_custom_rules():
    """Test defining multiple custom rules with different configurations."""
    LintrConfig = create_config_class()
    config = LintrConfig(
        github_token="test-token",
        rules={
            "strict_readme": {
                "base": "has_readme",
                "description": "Strict readme requirements",
                "config": {
                    "required_sections": ["Installation", "Usage", "Contributing"]
                },
            },
            "relaxed_readme": {
                "base": "has_readme",
                "description": "Relaxed readme requirements",
                "config": {"required_sections": ["Installation"]},
            },
        },
    )

    assert len(config.rules) == 2
    assert "strict_readme" in config.rules
    assert "relaxed_readme" in config.rules
    assert config.rules["strict_readme"].config["required_sections"] == [
        "Installation",
        "Usage",
        "Contributing",
    ]
    assert config.rules["relaxed_readme"].config["required_sections"] == [
        "Installation"
    ]


def test_custom_rule_in_ruleset():
    """Test using custom rules in rule sets."""
    LintrConfig = create_config_class()
    config = LintrConfig(
        github_token="test-token",
        rules={
            "custom_readme": {
                "base": "has_readme",
                "description": "Custom readme rule",
                "config": {"required_sections": ["Installation"]},
            }
        },
        rulesets={
            "custom_set": RuleSetConfig(
                description="custom_set", rules=["custom_readme", "has_license"]
            )
        },
    )

    assert "custom_set" in config.rulesets
    assert "custom_readme" in config.rulesets["custom_set"].rules
