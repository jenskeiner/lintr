"""Tests for GitHub API integration."""

import pytest
from unittest.mock import MagicMock, patch

from github import Auth, Github
from repolint.github import GitHubClient, GitHubConfig


@pytest.fixture
def mock_repo():
    """Create a mock GitHub repository."""
    repo = MagicMock()
    repo.name = "test-repo"
    repo.default_branch = "main"
    repo.description = "Test repository"
    repo.homepage = "https://example.com"
    repo.private = False
    repo.archived = False
    repo.has_issues = True
    repo.has_projects = True
    repo.has_wiki = True
    repo.allow_squash_merge = True
    repo.allow_merge_commit = True
    repo.allow_rebase_merge = True
    repo.delete_branch_on_merge = True
    return repo


@pytest.fixture
def github_config():
    """Create a GitHub configuration."""
    return GitHubConfig(token="test-token")


def test_github_config_validation():
    """Test GitHub configuration validation."""
    config = GitHubConfig(token="test-token")
    assert config.token == "test-token"
    assert config.org_name is None
    assert config.include_private is True
    assert config.include_archived is False


def test_get_user_repositories(github_config, mock_repo):
    """Test getting user repositories."""
    with patch('repolint.github.Github') as mock_github_class:
        # Setup mock
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]
        mock_github = MagicMock()
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github

        client = GitHubClient(github_config)
        repos = client.get_repositories()

        assert len(repos) == 1
        assert repos[0].name == "test-repo"
        mock_user.get_repos.assert_called_once()
        mock_github_class.assert_called_once()


def test_get_org_repositories(mock_repo):
    """Test getting organization repositories."""
    with patch('repolint.github.Github') as mock_github_class:
        # Setup config with org
        config = GitHubConfig(token="test-token", org_name="test-org")

        # Setup mock
        mock_org = MagicMock()
        mock_org.get_repos.return_value = [mock_repo]
        mock_github = MagicMock()
        mock_github.get_organization.return_value = mock_org
        mock_github_class.return_value = mock_github

        client = GitHubClient(config)
        repos = client.get_repositories()

        assert len(repos) == 1
        assert repos[0].name == "test-repo"
        mock_github.get_organization.assert_called_once_with("test-org")
        mock_org.get_repos.assert_called_once()
        mock_github_class.assert_called_once()


def test_get_repository_settings(github_config, mock_repo):
    """Test getting repository settings."""
    with patch('repolint.github.Github') as mock_github_class:
        mock_github = MagicMock()
        mock_github_class.return_value = mock_github

        client = GitHubClient(github_config)
        settings = client.get_repository_settings(mock_repo)

        assert settings["name"] == "test-repo"
        assert settings["default_branch"] == "main"
        assert settings["description"] == "Test repository"
        assert settings["homepage"] == "https://example.com"
        assert settings["private"] is False
        assert settings["archived"] is False
        assert settings["has_issues"] is True
        assert settings["has_projects"] is True
        assert settings["has_wiki"] is True
        assert settings["allow_squash_merge"] is True
        assert settings["allow_merge_commit"] is True
        assert settings["allow_rebase_merge"] is True
        assert settings["delete_branch_on_merge"] is True
        mock_github_class.assert_called_once()
