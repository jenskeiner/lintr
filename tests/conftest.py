"""Shared test fixtures for repolint."""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Any, Generator, List, Callable
from unittest.mock import MagicMock, patch

import pytest
import yaml
from github.Repository import Repository

from repolint.config import RepolintConfig
from repolint.github import GitHubClient


@pytest.fixture
def mock_config() -> Generator[Path, None, None]:
    """Create a temporary configuration file with the given configuration.
    
    This fixture creates a temporary YAML file with the provided configuration and
    yields its path. The file is automatically cleaned up after the test.
    
    Example:
        def test_with_custom_config(mock_config):
            config = {
                "github": {"token": "test-token"},
                "repository_filter": {
                    "include_patterns": ["test-*"],
                    "exclude_patterns": ["test-excluded"]
                },
                "rule_sets": [
                    {
                        "name": "test-ruleset",
                        "rules": ["R001", "R002"]
                    }
                ]
            }
            config_path = mock_config(config)
            # Use config_path in your test...
    """
    temp_file = NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    try:
        def _create_config(config: Dict[str, Any]) -> Path:
            yaml.safe_dump(config, temp_file)
            temp_file.flush()
            return Path(temp_file.name)
        
        yield _create_config
    finally:
        temp_file.close()
        os.unlink(temp_file.name)


@pytest.fixture
def mock_config_file(mock_config) -> Generator[Path, None, None]:
    """Create a temporary configuration file with default test configuration.
    
    This fixture provides a ready-to-use configuration file with sensible defaults
    for testing. Use this when you don't need to customize the configuration.
    """
    default_config = {
        "github": {
            "token": "test-token"
        },
        "repository_filter": {
            "include_patterns": ["test-*"],
            "exclude_patterns": []
        },
        "rule_sets": [
            {
                "name": "default",
                "rules": ["R001"]
            }
        ]
    }
    yield mock_config(default_config)


@pytest.fixture
def mock_github() -> Generator[Callable[[List[Dict[str, Any]], Dict[str, Dict[str, Any]]], None], None, None]:
    """Create a mock GitHub client with parameterizable repository responses.
    
    This fixture allows you to specify mock repositories and their settings that will be
    returned by the GitHub client in tests.
    
    Args:
        repositories: List of repository data dictionaries to mock
        settings: Dictionary mapping repository names to their settings
    
    Example:
        def test_with_mock_github(mock_github):
            # Define mock repository data
            mock_repos = [
                {
                    "name": "test-repo-1",
                    "private": False,
                    "archived": False
                },
                {
                    "name": "test-repo-2",
                    "private": True,
                    "archived": True
                }
            ]
            
            # Define mock settings for each repository
            mock_settings = {
                "test-repo-1": {
                    "default_branch": "main",
                    "has_issues": True,
                    "allow_squash_merge": True
                },
                "test-repo-2": {
                    "default_branch": "master",
                    "has_issues": False,
                    "allow_squash_merge": False
                }
            }
            
            # Set up the mock
            mock_github(mock_repos, mock_settings)
            
            # Your test code here...
    """
    def create_mock_repo(repo_data: Dict[str, Any]) -> MagicMock:
        mock_repo = MagicMock(spec=Repository)
        for key, value in repo_data.items():
            setattr(mock_repo, key, value)
        return mock_repo
    
    def setup_mock(repositories: List[Dict[str, Any]], settings: Dict[str, Dict[str, Any]]) -> None:
        mock_repos = [create_mock_repo(repo) for repo in repositories]
        
        # Mock get_repositories method
        def mock_get_repositories():
            return mock_repos
        
        # Mock get_repository_settings method
        def mock_get_repository_settings(repo):
            return settings.get(repo.name, {})
        
        with patch.object(GitHubClient, 'get_repositories', side_effect=mock_get_repositories), \
             patch.object(GitHubClient, 'get_repository_settings', side_effect=mock_get_repository_settings):
            yield
    
    return setup_mock
