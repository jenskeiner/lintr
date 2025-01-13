"""Configuration handling for repolint.

This module provides the configuration classes and functions for repolint.
Configuration can be loaded from multiple sources:
- .env file
- Environment variables
- Command-line arguments
- YAML configuration file
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RepositoryFilter(BaseModel):
    """Filter criteria for target repositories."""
    include_patterns: List[str] = Field(
        default_factory=list,
        description="List of glob patterns for repository names to include"
    )
    exclude_patterns: List[str] = Field(
        default_factory=list,
        description="List of glob patterns for repository names to exclude"
    )


class RuleSetConfig(BaseModel):
    """Configuration for a rule set."""
    name: str = Field(..., description="Name of the rule set")
    rules: List[str] = Field(
        default_factory=list,
        description="List of rule identifiers (e.g., R001) to include"
    )
    rule_sets: List[str] = Field(
        default_factory=list,
        description="List of other rule set names to include"
    )


class RepolintConfig(BaseSettings):
    """Main configuration class for repolint."""
    model_config = SettingsConfigDict(
        env_prefix="REPOLINT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
        env_parse_none_str="null",
        env_vars_override_env_file=True
    )

    # GitHub configuration
    github_token: str = Field(
        ...,
        description="GitHub personal access token",
        json_schema_extra={"env": ["GITHUB_TOKEN", "REPOLINT_GITHUB_TOKEN"]}
    )

    # Repository filtering
    repository_filter: Optional[RepositoryFilter] = Field(
        default=None,
        description="Filter criteria for target repositories"
    )

    # Rule sets
    default_rule_set: str = Field(
        "default",
        description="Name of the default rule set to use"
    )
    repository_rule_sets: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of repository names to rule set names"
    )
    rule_sets: Dict[str, RuleSetConfig] = Field(
        default_factory=dict,
        description="Custom rule set definitions"
    )

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "RepolintConfig":
        """Load configuration from a YAML file.
        
        Args:
            path: Path to the YAML configuration file.
            
        Returns:
            RepolintConfig: Configuration instance.
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist.
            yaml.YAMLError: If the YAML file is invalid.
            ValidationError: If the configuration is invalid.
        """
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required to load YAML configuration files. "
                "Install it with: pip install PyYAML"
            )

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls.model_validate(data)
