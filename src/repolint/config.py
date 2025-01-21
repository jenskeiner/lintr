"""Configuration management for repolint."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Type
import yaml

from pydantic import BaseModel, Field, ValidationError
from pydantic_core import PydanticCustomError
from pydantic_settings import (BaseSettings, PydanticBaseSettingsSource,
                             SettingsConfigDict)
from pydantic_settings.sources import YamlConfigSettingsSource


class RepositoryFilter(BaseModel):
    """Configuration for repository filtering."""

    include_patterns: List[str] = Field(default_factory=list)
    exclude_patterns: List[str] = Field(default_factory=list)


class RuleSetConfig(BaseModel):
    """Configuration for a rule set."""

    name: str
    rules: List[str] = Field(default_factory=list)
    rule_sets: List[str] = Field(default_factory=list)


class BaseRepolintConfig(BaseSettings):
    """Base configuration for repolint."""

    github_token: str = Field()
    default_rule_set: str = Field(default="empty")
    repository_filter: RepositoryFilter = Field(
        default_factory=RepositoryFilter,
    )
    rule_sets: Dict[str, RuleSetConfig] = Field(
        default_factory=dict,
    )
    repository_rule_sets: Dict[str, str] = Field(
        default_factory=dict,
    )

    model_config = SettingsConfigDict(
        env_prefix="REPOLINT_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="allow",
        env_ignore_empty=True,
    )


def create_config_class(yaml_file: Optional[Path] = None) -> Type[BaseRepolintConfig]:
    """Create a configuration class with a specific YAML file path.

    Args:
        yaml_file: Path to the YAML configuration file.

    Returns:
        A configuration class that includes the specified YAML file.

    Raises:
        FileNotFoundError: If yaml_file is specified but doesn't exist.
    """
    if yaml_file and not yaml_file.exists():
        raise FileNotFoundError(f"Config file not found: {yaml_file}")

    class RepolintConfig(BaseRepolintConfig):
        """Configuration for repolint."""

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            """Customize configuration sources.

            Priority (highest to lowest):
            1. Environment variables
            2. .env file
            3. YAML config file
            """
            if yaml_file:
                try:
                    yaml_settings = YamlConfigSettingsSource(
                        settings_cls=settings_cls,
                        yaml_file=yaml_file,
                    )
                    return (init_settings, env_settings, dotenv_settings, yaml_settings)
                except Exception as e:
                    raise ValidationError.from_exception_data(title="YAML parsing error", line_errors=[dict(type=PydanticCustomError("yaml_validation_error", "Error while parsing YAML file {file}", dict(file=yaml_file)))]) from e
            return (init_settings, env_settings, dotenv_settings)

    return RepolintConfig
