"""Test configuration and fixtures."""

import os
import tempfile
from pathlib import Path
from typing import Any
from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch


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
    monkeypatch.setenv("REPOLINT_GITHUB_TOKEN", "env-var-token")
    monkeypatch.setenv("REPOLINT_DEFAULT_RULE_SET", "env-var-ruleset")


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
        "REPOLINT_GITHUB_TOKEN=env-file-token\n"
        "REPOLINT_DEFAULT_RULE_SET=env-file-ruleset\n"
    )
    yield env_file
    env_file.unlink()


@pytest.fixture
def config_file() -> Generator[Path | None, None, None]:
    """Create a temporary configuration file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(
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
        f.flush()
        yield Path(f.name)
        os.unlink(f.name)


@pytest.fixture
def config(monkeypatch: MonkeyPatch) -> Generator[Any, None, None]:
    """Create a mocked configuration object with pre-defined properties."""
    # Create a mock config instance with pre-defined properties
    mock_config = MagicMock()
    mock_config.github_token = "token"
    mock_config.default_rule_set = "rule-set"
    mock_config.repository_filter = MagicMock()
    mock_config.rule_sets = {}
    mock_config.repository_rule_sets = {}

    # Create a mock config class that returns our pre-defined config
    mock_config_class = MagicMock()
    mock_config_class.return_value = mock_config

    # Mock the create_config_class function to return our mock class
    monkeypatch.setattr(
        "repolint.config.create_config_class", lambda *args, **kwargs: mock_config_class
    )

    yield mock_config


@pytest.fixture(autouse=True)
def temp_working_dir(monkeypatch: MonkeyPatch) -> Generator[Path, None, None]:
    """Create a temporary empty working directory for each test.

    This fixture is auto-used to ensure that every test runs in a clean directory,
    preventing interference between tests and avoiding conflicts with existing files.

    The directory is automatically cleaned up after each test.

    Returns:
        Path to the temporary working directory
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        monkeypatch.chdir(temp_dir_path)
        yield temp_dir_path


@pytest.fixture
def mock_repository():
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
def mock_github(monkeypatch, mock_repository):
    """Mock GitHub API responses.

    This fixture provides a flexible mock for GitHub API calls. It can be used
    in two ways:
    1. Simple mode: Returns a fixed list of repositories (default)
    2. Advanced mode: Allows for verifying method calls and customizing behavior
       by using the unittest.mock functionality
    """

    class MockGitHubClient:
        def __init__(self, *args, **kwargs):
            pass

        def get_repositories(self):
            # Return two repositories by default
            return [
                mock_repository,
                MagicMock(
                    name="test-repo-2",
                    private=True,
                    archived=True,
                    default_branch="master",
                    has_issues=False,
                    allow_squash_merge=False,
                ),
            ]

        def get_repository_settings(self, repo):
            # Return settings based on repository attributes
            return {
                "name": repo.name,
                "default_branch": repo.default_branch,
                "description": getattr(repo, "description", ""),
                "homepage": getattr(repo, "homepage", ""),
                "private": repo.private,
                "archived": repo.archived,
                "has_issues": getattr(repo, "has_issues", False),
                "has_projects": getattr(repo, "has_projects", False),
                "has_wiki": getattr(repo, "has_wiki", False),
                "allow_squash_merge": getattr(repo, "allow_squash_merge", False),
                "allow_merge_commit": getattr(repo, "allow_merge_commit", False),
                "allow_rebase_merge": getattr(repo, "allow_rebase_merge", False),
                "delete_branch_on_merge": getattr(
                    repo, "delete_branch_on_merge", False
                ),
            }

    monkeypatch.setattr("repolint.github.GitHubClient", MockGitHubClient)
    return MockGitHubClient
