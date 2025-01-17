"""Tests for core linting functionality."""

from unittest.mock import MagicMock

import pytest

from repolint.config import BaseRepolintConfig
from repolint.linter import Linter
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


def test_create_context(mock_repo, mock_config):
    """Test creating a rule context."""
    linter = Linter(mock_config)
    context = linter.create_context(mock_repo)
    assert isinstance(context, RuleContext)
    assert context.repository == mock_repo


def test_lint_repositories(mock_repo, mock_config):
    """Test linting repositories."""
    linter = Linter(mock_config)
    results = linter.lint_repositories([mock_repo])
    assert isinstance(results, dict)
    assert "test-repo" in results
    # Currently empty results as rule set application is not implemented yet
    assert results["test-repo"] == {}
