"""Tests for GitFlow branch naming rules."""

from unittest.mock import MagicMock, PropertyMock

from github.GithubException import GithubException

from repolint.rules.base import RuleResult
from repolint.rules.context import RuleContext
from repolint.rules.gitflow import GitFlowBranchNamingRule, GitFlowDefaultBranchRule


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


def test_gitflow_default_branch_valid():
    """Test that having develop as default branch passes."""
    mock_repo = MagicMock()
    mock_repo.default_branch = "develop"

    context = RuleContext(repository=mock_repo)
    rule = GitFlowDefaultBranchRule()
    result = rule.check(context)

    assert result.result == RuleResult.PASSED
    assert "correctly set to 'develop'" in result.message


def test_gitflow_default_branch_invalid():
    """Test that having a different default branch fails."""
    mock_repo = MagicMock()
    mock_repo.default_branch = "main"

    context = RuleContext(repository=mock_repo)
    rule = GitFlowDefaultBranchRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "should be 'develop'" in result.message
    assert result.fix_available


def test_gitflow_default_branch_github_exception():
    """Test handling of GitHub API exceptions."""
    mock_repo = MagicMock()
    type(mock_repo).default_branch = PropertyMock(
        side_effect=GithubException(status=404, data={"message": "Not Found"})
    )

    context = RuleContext(repository=mock_repo)
    rule = GitFlowDefaultBranchRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "Failed to check default branch" in result.message
    assert not result.fix_available


def test_gitflow_default_branch_fix_success():
    """Test successful fix of default branch."""
    mock_repo = MagicMock()
    mock_repo.default_branch = "main"
    mock_repo.get_branches.return_value = [create_mock_branch("develop")]

    context = RuleContext(repository=mock_repo)
    rule = GitFlowDefaultBranchRule()
    success = rule.fix(context)

    assert success
    mock_repo.edit.assert_called_once_with(default_branch="develop")


def test_gitflow_default_branch_fix_no_develop():
    """Test fix fails when develop branch doesn't exist."""
    mock_repo = MagicMock()
    mock_repo.default_branch = "main"
    mock_repo.get_branches.return_value = [create_mock_branch("main")]

    context = RuleContext(repository=mock_repo)
    rule = GitFlowDefaultBranchRule()
    success = rule.fix(context)

    assert not success
    mock_repo.edit.assert_not_called()


def test_gitflow_default_branch_fix_github_exception():
    """Test fix fails on GitHub API exception."""
    mock_repo = MagicMock()
    mock_repo.default_branch = "main"
    mock_repo.get_branches.return_value = [create_mock_branch("develop")]
    mock_repo.edit.side_effect = GithubException(
        status=404, data={"message": "Not Found"}
    )

    context = RuleContext(repository=mock_repo)
    rule = GitFlowDefaultBranchRule()
    success = rule.fix(context)

    assert not success
