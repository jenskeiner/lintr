"""Test configuration and fixtures."""

import os
import tempfile
from collections.abc import Callable
from collections.abc import Generator
from pathlib import Path
from typing import Any, TextIO
from unittest.mock import MagicMock, patch

import pytest
import yaml
from _pytest.monkeypatch import MonkeyPatch

from lintr.rules.base import Rule, RuleResult, RuleCheckResult, RuleContext


@pytest.fixture(autouse=True)
def empty_env(monkeypatch: MonkeyPatch) -> None:
    """Temporarily clear all environment variables for a test.

    This fixture removes all environment variables for the duration of a test,
    ensuring a completely clean environment. The original environment is automatically
    restored after the test completes.

    This is an autouse fixture, meaning it will automatically run for all tests
    to ensure a clean environment by default.
    """
    # Clear all environment variables
    for key in list(os.environ.keys()):
        monkeypatch.delenv(key)

    # The monkeypatch fixture will automatically restore the environment
    # when the test completes


@pytest.fixture
def env(monkeypatch: MonkeyPatch) -> None:
    """Set up a controlled test environment with known environment variables.

    This fixture ensures all tests run with a consistent environment setup.
    It should be used instead of directly manipulating environment variables.
    """
    # Set default test environment
    monkeypatch.setenv("LINTR_GITHUB_TOKEN", "env-var-token")
    monkeypatch.setenv("LINTR_DEFAULT_RULE_SET", "env-var-ruleset")


@pytest.fixture
def env_file() -> Generator[Path, None, None]:
    """Create a temporary .env file.

    Creates a .env file in the current working directory (which will be a temporary
    directory thanks to the temp_working_dir fixture) with test values for verifying
    configuration loading from .env files.

    The file is automatically cleaned up after the test completes.

    Returns:
        Path to the .env file
    """
    env_file = Path(".env")
    env_file.write_text(
        "LINTR_GITHUB_TOKEN=env-file-token\n"
        "LINTR_DEFAULT_RULE_SET=env-file-ruleset\n"
    )
    yield env_file
    env_file.unlink()


class TestConfigFile:
    def __init__(self, f: TextIO):
        self._f = f

    @property
    def path(self) -> Path:
        return Path(self._f.name)

    def set(self, content: dict | str) -> None:
        self._f.seek(0)  # Go to beginning of file
        if isinstance(content, dict):
            yaml.dump(content, self._f)
        else:
            self._f.write(content)
        self._f.truncate()  # Remove any remaining content
        self._f.flush()  # Ensure content is written to disk


@pytest.fixture
def config_file() -> Generator[TestConfigFile, None, None]:
    """Create a temporary configuration file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        c = TestConfigFile(f)
        c.set(
            """
github_token: yaml-token
default_rule_set: yaml-ruleset
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
"""
        )
        f.close()
        yield c
        os.unlink(f.name)


@pytest.fixture
def config(monkeypatch: MonkeyPatch) -> Generator[Any, None, None]:
    """Create a mocked configuration object with pre-defined properties."""
    # Create a mock config instance with pre-defined properties
    mock_config = MagicMock()
    mock_config.github_token = "token"
    mock_config.default_rule_set = "empty"
    mock_config.repository_filter = None
    mock_config.rule_sets = {}
    mock_config.repository_rule_sets = {}
    mock_config.rules = {}

    # Create a mock config class that returns our pre-defined config
    mock_config_class = MagicMock()
    mock_config_class.return_value = mock_config

    # Mock the create_config_class function to return our mock class
    monkeypatch.setattr(
        "lintr.config.create_config_class", lambda *args, **kwargs: mock_config_class
    )

    yield mock_config


@pytest.fixture
def repository():
    """Create a mock GitHub repository."""
    repo = MagicMock()
    repo.name = "test-repo"
    repo.private = False
    repo.archived = False
    repo.default_branch = "main"
    repo.description = "Test repository"
    repo.homepage = "https://example.com"
    repo.has_issues = True
    repo.has_projects = True
    repo.has_wiki = True
    repo.allow_squash_merge = True
    repo.allow_merge_commit = True
    repo.allow_rebase_merge = True
    repo.delete_branch_on_merge = True
    return repo


@pytest.fixture
def mock_github(monkeypatch):
    """Mock GitHub API responses."""

    class MockRepository:
        def __init__(self, name, private=False, archived=False):
            self.name = name
            self.private = private
            self.archived = archived

    class MockGitHubClient:
        def __init__(self, *args, **kwargs):
            pass

        def get_repositories(self):
            return [
                MockRepository("test-repo-1", private=False, archived=False),
                MockRepository("test-repo-2", private=True, archived=True),
            ]

    monkeypatch.setattr("lintr.gh.GitHubClient", MockGitHubClient)
    return MockGitHubClient


@pytest.fixture
def rule_cls() -> (
    Callable[
        [
            str,
            str,
            RuleResult
            | RuleCheckResult
            | Exception
            | Callable[[RuleContext], RuleCheckResult]
            | None,
            Callable[[RuleContext], tuple[bool, str]] | None,
        ],
        type[Rule],
    ]
):
    def fn(
        rule_id: str,
        description: str,
        result: RuleResult
        | RuleCheckResult
        | Exception
        | Callable[[RuleContext], RuleCheckResult] = RuleCheckResult(
            RuleResult.PASSED, "Test passed"
        ),
        fix: Callable[[RuleContext], tuple[bool, str]] | None = None,
    ) -> type[Rule]:
        class R(Rule):
            _id = rule_id
            _description = description

            def check(self, context: RuleContext) -> RuleCheckResult:
                if isinstance(result, RuleResult):
                    return RuleCheckResult(result, "Test passed")
                elif isinstance(result, RuleCheckResult):
                    return result
                elif isinstance(result, Exception):
                    raise result
                else:
                    return result(context)

            def fix(self, context: RuleContext) -> tuple[bool, str]:
                if fix is not None:
                    return fix(context)
                else:
                    return super().fix(context)

        return R

    return fn


@pytest.fixture
def rule_manager():
    """Create a mock rule manager."""
    with patch("lintr.linter.RuleManager") as mock_manager_class:
        # Setup mock rule manager
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        yield mock_manager
