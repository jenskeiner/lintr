"""Tests for GitFlow branch naming rules."""

from unittest.mock import MagicMock

from github.GithubException import GithubException

from repolint.rules.base import RuleResult
from repolint.rules.context import RuleContext
from repolint.rules.gitflow import GitFlowBranchNamingRule


def create_mock_branch(name: str) -> MagicMock:
    """Create a mock branch with the given name."""
    branch = MagicMock()
    branch.name = name
    return branch


def test_gitflow_branch_naming_valid():
    """Test that valid GitFlow branch names pass."""
    # Create mock repository with valid branch names
    mock_repo = MagicMock()
    mock_repo.get_branches.return_value = [
        create_mock_branch("main"),
        create_mock_branch("develop"),
        create_mock_branch("feature/add-auth"),
        create_mock_branch("release/1.0.0"),
        create_mock_branch("hotfix/security-patch"),
        create_mock_branch("support/legacy-api"),
        create_mock_branch("dependabot/npm_and_yarn/lodash-4.17.21"),
    ]

    context = RuleContext(repository=mock_repo)
    rule = GitFlowBranchNamingRule()
    result = rule.check(context)

    assert result.result == RuleResult.PASSED
    assert "All branch names conform to GitFlow conventions" in result.message


def test_gitflow_branch_naming_missing_main():
    """Test that missing main/master branch fails."""
    mock_repo = MagicMock()
    mock_repo.get_branches.return_value = [
        create_mock_branch("develop"),
        create_mock_branch("feature/add-auth"),
    ]

    context = RuleContext(repository=mock_repo)
    rule = GitFlowBranchNamingRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "must have either 'main' or 'master' branch" in result.message


def test_gitflow_branch_naming_missing_develop():
    """Test that missing develop branch fails."""
    mock_repo = MagicMock()
    mock_repo.get_branches.return_value = [
        create_mock_branch("main"),
        create_mock_branch("feature/add-auth"),
    ]

    context = RuleContext(repository=mock_repo)
    rule = GitFlowBranchNamingRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "must have a 'develop' branch" in result.message


def test_gitflow_branch_naming_invalid_names():
    """Test that invalid branch names fail."""
    mock_repo = MagicMock()
    mock_repo.get_branches.return_value = [
        create_mock_branch("main"),
        create_mock_branch("develop"),
        create_mock_branch("invalid-branch"),
        create_mock_branch("feat/something"),  # Wrong prefix
    ]

    context = RuleContext(repository=mock_repo)
    rule = GitFlowBranchNamingRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "do not follow GitFlow naming conventions" in result.message
    assert "invalid-branch" in result.message
    assert "feat/something" in result.message


def test_gitflow_branch_naming_github_exception():
    """Test handling of GitHub API exceptions."""
    mock_repo = MagicMock()
    mock_repo.get_branches.side_effect = GithubException(
        status=404, data={"message": "Not Found"}
    )

    context = RuleContext(repository=mock_repo)
    rule = GitFlowBranchNamingRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "Failed to check branch names" in result.message
