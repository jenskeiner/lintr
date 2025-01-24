"""Test configuration and fixtures."""

import os
import tempfile
from pathlib import Path
from typing import Any
from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from repolint.config import create_config_class


@pytest.fixture
def config_file() -> Generator[Path | None, None, None]:
    """Create a temporary configuration file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(
            """
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
"""
        )
        f.flush()
        yield Path(f.name)
        os.unlink(f.name)


@pytest.fixture
def test_env(monkeypatch: MonkeyPatch) -> None:
    """Set up a controlled test environment with known environment variables.

    This fixture ensures all tests run with a consistent environment setup.
    It should be used instead of directly manipulating environment variables.
    """
    # Clear any existing environment variables we care about
    env_vars_to_clear = [
        "GITHUB_TOKEN",
        "REPOLINT_GITHUB_TOKEN",
    ]
    for var in env_vars_to_clear:
        monkeypatch.delenv(var, raising=False)

    # Set default test environment
    monkeypatch.setenv("REPOLINT_GITHUB_TOKEN", "env-token")


@pytest.fixture
def config(
    config_file: Path, test_env, monkeypatch: MonkeyPatch
) -> Generator[Any, None, None]:
    """Create a configuration object with controlled environment."""
    # Create config class with the temporary file
    RepolintConfig = create_config_class(yaml_file=config_file)
    yield RepolintConfig()


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
