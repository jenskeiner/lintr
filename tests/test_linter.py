"""Tests for core linting functionality."""

from unittest.mock import MagicMock, patch

import pytest

from repolint.config import BaseRepolintConfig
from repolint.linter import Linter
from repolint.rules import RuleSet
from repolint.rules.base import Rule, RuleCheckResult, RuleResult
from repolint.rules.context import RuleContext


class MockRule(Rule):
    """Mock rule for testing."""
    def check(self, context: RuleContext) -> RuleCheckResult:
        """Return a mock check result."""
        return RuleCheckResult(
            result=RuleResult.PASSED,
            message="Mock rule passed",
            fix_available=False
        )


class FailingMockRule(Rule):
    """Mock rule that fails during execution."""
    def check(self, context: RuleContext) -> RuleCheckResult:
        """Raise an exception."""
        raise Exception("Rule execution failed")


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
    rule_set = RuleSet("default", "Default rule set")
    rule_set.add_rule(MockRule("R001", "Test rule"))
    return rule_set


@pytest.fixture
def mock_rule_manager():
    """Create a mock rule manager."""
    with patch('repolint.linter.RuleManager') as mock_manager_class:
        # Setup mock rule manager
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        yield mock_manager


def test_rule_set_rules_ordering():
    """Test that rules are returned in order by rule_id."""
    # Create a rule set with rules in non-alphabetical order
    rule_set = RuleSet("test", "Test rule set")
    rule_set.add_rule(MockRule("R002", "Second rule"))
    rule_set.add_rule(MockRule("R001", "First rule"))
    rule_set.add_rule(MockRule("R003", "Third rule"))

    # Get rules and verify order
    rules = list(rule_set.rules())
    assert len(rules) == 3
    assert [r.rule_id for r in rules] == ["R001", "R002", "R003"]


def test_rule_set_rules_uniqueness():
    """Test that duplicate rules are handled correctly."""
    # Create nested rule sets with duplicate rules
    parent = RuleSet("parent", "Parent rule set")
    child = RuleSet("child", "Child rule set")
    grandchild = RuleSet("grandchild", "Grandchild rule set")

    # Add rules to each level
    parent.add_rule(MockRule("R001", "First rule - parent"))
    child.add_rule(MockRule("R001", "First rule - child"))  # Duplicate ID
    child.add_rule(MockRule("R002", "Second rule - child"))
    grandchild.add_rule(MockRule("R002", "Second rule - grandchild"))  # Duplicate ID
    grandchild.add_rule(MockRule("R003", "Third rule - grandchild"))

    # Link rule sets
    child.add_rule_set(grandchild)
    parent.add_rule_set(child)

    # Get rules and verify uniqueness and order
    rules = list(parent.rules())
    assert len(rules) == 3  # Should only have 3 unique rules
    assert [r.rule_id for r in rules] == ["R001", "R002", "R003"]
    # First occurrence of each rule should be kept
    assert rules[0].description == "First rule - parent"
    assert rules[1].description == "Second rule - child"
    assert rules[2].description == "Third rule - grandchild"


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


def test_check_repository_success(mock_repo, mock_config, mock_rule_set):
    """Test successful repository checking."""
    # Create linter and check repository
    linter = Linter(mock_config)
    results = linter.check_repository(mock_repo, mock_rule_set)

    # Verify results
    assert "R001" in results
    assert results["R001"].result == RuleResult.PASSED
    assert results["R001"].message == "Mock rule passed"
    assert not results["R001"].fix_available


def test_check_repository_rule_error(mock_repo, mock_config):
    """Test handling of rule execution errors."""
    # Create a rule set with a failing rule
    rule_set = RuleSet("test", "Test rule set")
    rule_set.add_rule(FailingMockRule("R001", "Failing test rule"))

    # Create linter and check repository
    linter = Linter(mock_config)
    results = linter.check_repository(mock_repo, rule_set)

    # Verify error is reported in results
    assert "R001" in results
    assert results["R001"].result == RuleResult.FAILED
    assert "Rule execution failed" in results["R001"].message


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


def test_lint_repositories_success(mock_repo, mock_config, mock_rule_set, mock_rule_manager):
    """Test successful repository linting."""
    # Setup mock rule manager
    mock_rule_manager.get_rule_set.return_value = mock_rule_set

    # Create linter and lint repositories
    linter = Linter(mock_config)
    results = linter.lint_repositories([mock_repo])

    # Verify results
    assert "test-repo" in results
    repo_results = results["test-repo"]
    assert "R001" in repo_results
    assert repo_results["R001"].result == RuleResult.PASSED
    assert repo_results["R001"].message == "Mock rule passed"
    assert not repo_results["R001"].fix_available
