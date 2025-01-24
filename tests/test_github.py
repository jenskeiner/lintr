"""Tests for GitHub API integration."""

import pytest
from unittest.mock import MagicMock, patch

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
    with patch("repolint.github.Github") as mock_github_class:
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
        mock_user.get_repos.assert_called_once_with(affiliation="owner")
        mock_github_class.assert_called_once()


def test_get_org_repositories(mock_repo):
    """Test getting organization repositories."""
    with patch("repolint.github.Github") as mock_github_class:
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
    with patch("repolint.github.Github") as mock_github_class:
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


def test_repository_filtering_with_include_patterns(github_config, mock_repo):
    """Test repository filtering with include patterns."""
    # Create additional mock repos
    mock_repo2 = MagicMock()
    mock_repo2.name = "test-api"
    mock_repo2.private = False
    mock_repo2.archived = False

    mock_repo3 = MagicMock()
    mock_repo3.name = "demo-app"
    mock_repo3.private = False
    mock_repo3.archived = False

    # Set up include patterns to match only test-* repositories
    github_config.repository_filter.include_patterns = ["test-*"]

    with patch("repolint.github.Github") as mock_github_class:
        # Setup mock
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo, mock_repo2, mock_repo3]
        mock_github = MagicMock()
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github

        # Create client and get repositories
        client = GitHubClient(github_config)
        repos = client.get_repositories()

        # Verify only repositories matching the pattern are returned
        assert len(repos) == 2
        repo_names = [repo.name for repo in repos]
        assert "test-repo" in repo_names
        assert "test-api" in repo_names
        assert "demo-app" not in repo_names


def test_repository_filtering_with_exclude_patterns(github_config, mock_repo):
    """Test repository filtering with exclude patterns."""
    # Create additional mock repos
    mock_repo2 = MagicMock()
    mock_repo2.name = "test-api"
    mock_repo2.private = False
    mock_repo2.archived = False

    mock_repo3 = MagicMock()
    mock_repo3.name = "demo-app"
    mock_repo3.private = False
    mock_repo3.archived = False

    # Set up exclude patterns to exclude test-* repositories
    github_config.repository_filter.exclude_patterns = ["test-*"]

    with patch("repolint.github.Github") as mock_github_class:
        # Setup mock
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo, mock_repo2, mock_repo3]
        mock_github = MagicMock()
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github

        # Create client and get repositories
        client = GitHubClient(github_config)
        repos = client.get_repositories()

        # Verify only non-excluded repositories are returned
        assert len(repos) == 1
        assert repos[0].name == "demo-app"


def test_repository_filtering_with_both_patterns(github_config, mock_repo):
    """Test repository filtering with both include and exclude patterns."""
    # Create additional mock repos
    mock_repo2 = MagicMock()
    mock_repo2.name = "test-api"
    mock_repo2.private = False
    mock_repo2.archived = False

    mock_repo3 = MagicMock()
    mock_repo3.name = "test-demo"
    mock_repo3.private = False
    mock_repo3.archived = False

    mock_repo4 = MagicMock()
    mock_repo4.name = "demo-app"
    mock_repo4.private = False
    mock_repo4.archived = False

    # Set up patterns to include test-* but exclude *-api
    github_config.repository_filter.include_patterns = ["test-*"]
    github_config.repository_filter.exclude_patterns = ["*-api"]

    with patch("repolint.github.Github") as mock_github_class:
        # Setup mock
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [
            mock_repo,
            mock_repo2,
            mock_repo3,
            mock_repo4,
        ]
        mock_github = MagicMock()
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github

        # Create client and get repositories
        client = GitHubClient(github_config)
        repos = client.get_repositories()

        # Verify only repositories matching include but not exclude are returned
        assert len(repos) == 2
        repo_names = [repo.name for repo in repos]
        assert "test-repo" in repo_names
        assert "test-demo" in repo_names
        assert "test-api" not in repo_names
        assert "demo-app" not in repo_names


def test_include_organisation_repositories(github_config, mock_repo):
    """Test including organisation repositories."""
    with patch("repolint.github.Github") as mock_github_class:
        # Test with include_organisations=True
        mock_org = MagicMock()
        mock_org.get_repos.return_value = [mock_repo]

        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]
        mock_user.get_orgs.return_value = [mock_org]

        mock_github = MagicMock()
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github

        config = GitHubConfig(token="test-token", include_organisations=True)
        client = GitHubClient(config)
        repos = client.get_repositories()

        # Should get both user and org repos
        assert len(repos) == 2
        mock_user.get_repos.assert_called_once_with(affiliation="owner")
        mock_user.get_orgs.assert_called_once()
        mock_org.get_repos.assert_called_once()

        # Reset mocks for next test
        mock_github_class.reset_mock()
        mock_github = MagicMock()
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github

        # Test with include_organisations=False
        config = GitHubConfig(token="test-token", include_organisations=False)
        client = GitHubClient(config)
        repos = client.get_repositories()

        # Should only get user repos
        assert len(repos) == 1
        mock_user.get_repos.assert_called_once_with(affiliation="owner")
        mock_user.get_orgs.assert_not_called()
