"""Tests for branch-related rules."""

from unittest.mock import MagicMock

import pytest
from github.GithubException import GithubException

from repolint.rules.base import RuleResult
from repolint.rules.branch_rules import DefaultBranchExistsRule


def test_default_branch_exists_rule_init():
    """Test initialization of DefaultBranchExistsRule."""
    rule = DefaultBranchExistsRule()
    assert rule.rule_id == "R001"
    assert "default branch" in rule.description.lower()


def test_default_branch_exists_rule_check_success():
    """Test DefaultBranchExistsRule when repository has a default branch."""
    # Create a mock repository with a default branch
    repo = MagicMock()
    repo.default_branch = "main"

    # Check the rule
    rule = DefaultBranchExistsRule()
    result = rule.check(repo)

    assert result.result == RuleResult.PASSED
    assert "main" in result.message
    assert not result.fix_available
    assert result.fix_description is None


def test_default_branch_exists_rule_check_failure():
    """Test DefaultBranchExistsRule when repository has no default branch."""
    # Create a mock repository without a default branch
    repo = MagicMock()
    repo.default_branch = None

    # Check the rule
    rule = DefaultBranchExistsRule()
    result = rule.check(repo)

    assert result.result == RuleResult.FAILED
    assert "does not have" in result.message.lower()
    assert not result.fix_available
    assert "create a branch" in result.fix_description.lower()


def test_default_branch_exists_rule_check_error():
    """Test DefaultBranchExistsRule when GitHub API call fails."""
    # Create a mock repository that raises an exception
    repo = MagicMock()
    repo.default_branch = MagicMock(
        side_effect=GithubException(404, "Not found")
    )

    # Check the rule
    rule = DefaultBranchExistsRule()
    result = rule.check(repo)

    assert result.result == RuleResult.FAILED
    assert "failed to check" in result.message.lower()
    assert "not found" in result.message.lower()
    assert not result.fix_available
    assert result.fix_description is None
