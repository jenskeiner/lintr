"""Configuration management for lintr."""

from pathlib import Path

from pydantic import BaseModel, Field, ValidationError
from pydantic_core import PydanticCustomError
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
from pydantic_settings.sources import YamlConfigSettingsSource


class RepositoryFilter(BaseModel):
    """Configuration for repository filtering."""

    include_patterns: list[str] = Field(default_factory=list)
    exclude_patterns: list[str] = Field(default_factory=list)


class RuleSetConfig(BaseModel):
    """Configuration for a rule set."""

    name: str
    rules: list[str] = Field(default_factory=list)
    rule_sets: list[str] = Field(default_factory=list)


class CustomRuleDefinition(BaseModel):
    base: str
    description: str
    config: dict


class RepositoryConfig(BaseModel):
    ruleset: str | None = None
    rules: dict[str, dict] = Field(default_factory=dict)


class BaseLintrConfig(BaseSettings):
    """Base configuration for lintr."""

    github_token: str = Field()

    repository_filter: RepositoryFilter = Field(
        default_factory=RepositoryFilter,
    )

    # Custom rules.
    rules: dict[str, CustomRuleDefinition] = Field(default_factory=dict)

    rule_sets: dict[str, RuleSetConfig] = Field(
        default_factory=dict,
    )

    default_rule_set: str = Field(default="empty")

    repository_rule_sets: dict[str, RepositoryConfig] = Field(
        default_factory=dict,
    )

    model_config = SettingsConfigDict(
        env_prefix="LINTR_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="allow",
        env_ignore_empty=True,
    )


def create_config_class(yaml_file: Path | None = None) -> type[BaseLintrConfig]:
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

    class LintrConfig(BaseLintrConfig):
        """Configuration for lintr."""

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
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
                    raise ValidationError.from_exception_data(
                        title="YAML parsing error",
                        line_errors=[
                            dict(
                                type=PydanticCustomError(
                                    "yaml_validation_error",
                                    "Error while parsing YAML file {file}",
                                    dict(file=yaml_file),
                                )
                            )
                        ],
                    ) from e
            return (init_settings, env_settings, dotenv_settings)

    return LintrConfig
