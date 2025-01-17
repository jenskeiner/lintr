"""Tests for core linting functionality."""

from unittest.mock import MagicMock, patch

import pytest

from repolint.config import BaseRepolintConfig
from repolint.linter import Linter
from repolint.rules import RuleSet
from repolint.rules.context import RuleContext


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
    return repo


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock(spec=BaseRepolintConfig)
    config.default_rule_set = "default"
    config.repository_filter = None
    config.rule_sets = {}
    config.repository_rule_sets = {}
    return config


@pytest.fixture
def mock_rule_set():
    """Create a mock rule set."""
    rule_set = MagicMock(spec=RuleSet)
    rule_set.rule_set_id = "default"
    rule_set.description = "Default rule set"
    return rule_set


@pytest.fixture
def mock_rule_manager():
    """Create a mock rule manager."""
    with patch('repolint.linter.RuleManager') as mock_manager_class:
        # Setup mock rule manager
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        yield mock_manager


def test_create_context(mock_repo, mock_config):
    """Test creating a rule context."""
    linter = Linter(mock_config)
    context = linter.create_context(mock_repo)
    assert isinstance(context, RuleContext)
    assert context.repository == mock_repo


def test_get_rule_set_for_repository_default(mock_repo, mock_config, mock_rule_set, mock_rule_manager):
    """Test getting default rule set for repository."""
    # Setup mock rule manager
    mock_rule_manager.get_rule_set.return_value = mock_rule_set

    # Create linter and get rule set
    linter = Linter(mock_config)
    rule_set_info = linter.get_rule_set_for_repository(mock_repo)

    # Verify correct rule set is returned
    assert rule_set_info is not None
    rule_set_id, rule_set = rule_set_info
    assert rule_set_id == "default"
    assert rule_set == mock_rule_set
    mock_rule_manager.get_rule_set.assert_called_once_with("default")


def test_get_rule_set_for_repository_specific(mock_repo, mock_config, mock_rule_set, mock_rule_manager):
    """Test getting repository-specific rule set."""
    # Configure repository-specific rule set
    mock_config.repository_rule_sets = {"test-repo": "specific"}
    mock_rule_set.rule_set_id = "specific"

    # Setup mock rule manager
    mock_rule_manager.get_rule_set.return_value = mock_rule_set

    # Create linter and get rule set
    linter = Linter(mock_config)
    rule_set_info = linter.get_rule_set_for_repository(mock_repo)

    # Verify correct rule set is returned
    assert rule_set_info is not None
    rule_set_id, rule_set = rule_set_info
    assert rule_set_id == "specific"
    assert rule_set == mock_rule_set
    mock_rule_manager.get_rule_set.assert_called_once_with("specific")


def test_get_rule_set_for_repository_not_found(mock_repo, mock_config, mock_rule_manager):
    """Test handling of non-existent rule set."""
    # Setup mock rule manager to return no rule set
    mock_rule_manager.get_rule_set.return_value = None

    # Create linter and get rule set
    linter = Linter(mock_config)
    rule_set_info = linter.get_rule_set_for_repository(mock_repo)

    # Verify no rule set is returned
    assert rule_set_info is None
    mock_rule_manager.get_rule_set.assert_called_once_with("default")


def test_lint_repositories_with_missing_rule_set(mock_repo, mock_config, mock_rule_manager):
    """Test linting repositories when rule set is not found."""
    # Setup mock rule manager to return no rule set
    mock_rule_manager.get_rule_set.return_value = None

    # Create linter and lint repositories
    linter = Linter(mock_config)
    results = linter.lint_repositories([mock_repo])

    # Verify error is reported in results
    assert "test-repo" in results
    assert "error" in results["test-repo"]
    assert "No rule set found" in results["test-repo"]["error"]
    mock_rule_manager.get_rule_set.assert_called_once_with("default")


def test_lint_repositories(mock_repo, mock_config, mock_rule_set, mock_rule_manager):
    """Test linting repositories."""
    # Setup mock rule manager
    mock_rule_manager.get_rule_set.return_value = mock_rule_set

    # Create linter and lint repositories
    linter = Linter(mock_config)
    results = linter.lint_repositories([mock_repo])

    # Verify results
    assert isinstance(results, dict)
    assert "test-repo" in results
    assert results["test-repo"] == {}
