"""Tests for branch-related rules."""

from unittest.mock import MagicMock, PropertyMock
from github.GithubException import GithubException

from lintr.rules.base import RuleResult
from lintr.rules.branch_rules import (
    DefaultBranchExistsRule,
    WebCommitSignoffRequiredRule,
    DeleteBranchOnMergeRule,
    AutoMergeDisabledRule,
)
from lintr.rules.context import RuleContext


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
    context = RuleContext(repository=repo)

    # Check the rule
    rule = DefaultBranchExistsRule()
    result = rule.check(context)

    assert result.result == RuleResult.PASSED
    assert "main" in result.message
    assert not result.fix_available
    assert result.fix_description is None


def test_default_branch_exists_rule_check_failure():
    """Test DefaultBranchExistsRule when repository has no default branch."""
    # Create a mock repository without a default branch
    repo = MagicMock()
    repo.default_branch = None
    context = RuleContext(repository=repo)

    # Check the rule
    rule = DefaultBranchExistsRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "does not have" in result.message.lower()
    assert not result.fix_available
    assert "create a branch" in result.fix_description.lower()


def test_default_branch_exists_rule_check_error():
    """Test DefaultBranchExistsRule when GitHub API call fails."""
    # Create a mock repository that raises an exception
    repo = MagicMock()
    repo.default_branch = MagicMock(side_effect=GithubException(404, "Not found"))
    context = RuleContext(repository=repo)

    # Check the rule
    rule = DefaultBranchExistsRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "failed to check" in result.message.lower()
    assert "not found" in result.message.lower()
    assert not result.fix_available
    assert result.fix_description is None


def test_web_commit_signoff_required_rule_init():
    """Test initialization of WebCommitSignoffRequiredRule."""
    rule = WebCommitSignoffRequiredRule()
    assert rule.rule_id == "R004"
    assert "web-based commits" in rule.description.lower()


def test_web_commit_signoff_required_rule_check_success():
    """Test WebCommitSignoffRequiredRule when signoff is required."""
    # Create a mock repository with web commit signoff required
    repo = MagicMock()
    repo.web_commit_signoff_required = True
    context = RuleContext(repository=repo)

    # Check the rule
    rule = WebCommitSignoffRequiredRule()
    result = rule.check(context)

    assert result.result == RuleResult.PASSED
    assert "requires signoff" in result.message.lower()
    assert not result.fix_available
    assert result.fix_description is None


def test_web_commit_signoff_required_rule_check_failure():
    """Test WebCommitSignoffRequiredRule when signoff is not required."""
    # Create a mock repository without web commit signoff required
    repo = MagicMock()
    repo.web_commit_signoff_required = False
    context = RuleContext(repository=repo)

    # Check the rule
    rule = WebCommitSignoffRequiredRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "does not require signoff" in result.message.lower()
    assert result.fix_available
    assert "enable" in result.fix_description.lower()


def test_web_commit_signoff_required_rule_check_error():
    """Test WebCommitSignoffRequiredRule when GitHub API call fails."""
    # Create a mock repository that raises an exception
    repo = MagicMock()
    type(repo).web_commit_signoff_required = PropertyMock(
        side_effect=GithubException(404, "Not found")
    )
    context = RuleContext(repository=repo)

    # Check the rule
    rule = WebCommitSignoffRequiredRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "error checking" in result.message.lower()
    assert "not found" in result.message.lower()
    assert not result.fix_available
    assert result.fix_description is None


def test_web_commit_signoff_required_rule_fix_success():
    """Test WebCommitSignoffRequiredRule fix method when successful."""
    # Create a mock repository
    repo = MagicMock()
    context = RuleContext(repository=repo)

    # Fix the issue
    rule = WebCommitSignoffRequiredRule()
    success, message = rule.fix(context)

    assert success
    assert "enabled" in message.lower()
    repo.edit.assert_called_once_with(web_commit_signoff_required=True)


def test_web_commit_signoff_required_rule_fix_error():
    """Test WebCommitSignoffRequiredRule fix method when GitHub API call fails."""
    # Create a mock repository that raises an exception
    repo = MagicMock()
    repo.edit.side_effect = GithubException(404, "Not found")
    context = RuleContext(repository=repo)

    # Try to fix
    rule = WebCommitSignoffRequiredRule()
    success, message = rule.fix(context)

    assert not success
    assert "failed to enable" in message.lower()
    assert "not found" in message.lower()
    repo.edit.assert_called_once_with(web_commit_signoff_required=True)


def test_delete_branch_on_merge_rule_init():
    """Test initialization of DeleteBranchOnMergeRule."""
    rule = DeleteBranchOnMergeRule()
    assert rule.rule_id == "R017"
    assert "delete_branch_on_merge" in rule.description.lower()


def test_delete_branch_on_merge_rule_check_success():
    """Test DeleteBranchOnMergeRule when delete_branch_on_merge is enabled."""
    # Create a mock repository with delete_branch_on_merge enabled
    repo = MagicMock()
    repo.delete_branch_on_merge = True
    context = RuleContext(repository=repo)

    # Check the rule
    rule = DeleteBranchOnMergeRule()
    result = rule.check(context)

    assert result.result == RuleResult.PASSED
    assert "enabled" in result.message.lower()
    assert not result.fix_available
    assert result.fix_description is None


def test_delete_branch_on_merge_rule_check_failure():
    """Test DeleteBranchOnMergeRule when delete_branch_on_merge is disabled."""
    # Create a mock repository with delete_branch_on_merge disabled
    repo = MagicMock()
    repo.delete_branch_on_merge = False
    context = RuleContext(repository=repo)

    # Check the rule
    rule = DeleteBranchOnMergeRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "not" in result.message.lower()
    assert result.fix_available
    assert "enable" in result.fix_description.lower()


def test_delete_branch_on_merge_rule_check_error():
    """Test DeleteBranchOnMergeRule when GitHub API call fails."""
    # Create a mock repository that raises an exception
    repo = MagicMock()
    type(repo).delete_branch_on_merge = PropertyMock(
        side_effect=GithubException(404, "Not found")
    )
    context = RuleContext(repository=repo)

    # Check the rule
    rule = DeleteBranchOnMergeRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "error" in result.message.lower()
    assert "not found" in result.message.lower()
    assert not result.fix_available
    assert result.fix_description is None


def test_delete_branch_on_merge_rule_fix_success():
    """Test DeleteBranchOnMergeRule fix method when successful."""
    # Create a mock repository
    repo = MagicMock()
    context = RuleContext(repository=repo)

    # Fix the rule
    rule = DeleteBranchOnMergeRule()
    success, message = rule.fix(context)

    assert success is True
    assert "enabled" in message.lower()
    repo.edit.assert_called_once_with(delete_branch_on_merge=True)


def test_delete_branch_on_merge_rule_fix_error():
    """Test DeleteBranchOnMergeRule fix method when GitHub API call fails."""
    # Create a mock repository that raises an exception
    repo = MagicMock()
    repo.edit.side_effect = GithubException(404, "Not found")
    context = RuleContext(repository=repo)

    # Fix the rule
    rule = DeleteBranchOnMergeRule()
    success, message = rule.fix(context)

    assert success is False
    assert "failed" in message.lower()
    assert "not found" in message.lower()
    repo.edit.assert_called_once_with(delete_branch_on_merge=True)


def test_auto_merge_disabled_rule_init():
    """Test initialization of AutoMergeDisabledRule."""
    rule = AutoMergeDisabledRule()
    assert rule.rule_id == "R018"
    assert "auto merge" in rule.description.lower()


def test_auto_merge_disabled_rule_check_success():
    """Test AutoMergeDisabledRule when auto merge is disabled."""
    # Create a mock repository with auto merge disabled
    repo = MagicMock()
    repo.allow_auto_merge = False
    context = RuleContext(repository=repo)

    # Check the rule
    rule = AutoMergeDisabledRule()
    result = rule.check(context)

    assert result.result == RuleResult.PASSED
    assert "disabled" in result.message.lower()
    assert not result.fix_available
    assert result.fix_description is None


def test_auto_merge_disabled_rule_check_failure():
    """Test AutoMergeDisabledRule when auto merge is enabled."""
    # Create a mock repository with auto merge enabled
    repo = MagicMock()
    repo.allow_auto_merge = True
    context = RuleContext(repository=repo)

    # Check the rule
    rule = AutoMergeDisabledRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "enabled" in result.message.lower()
    assert result.fix_available
    assert "disable" in result.fix_description.lower()


def test_auto_merge_disabled_rule_check_error():
    """Test AutoMergeDisabledRule when GitHub API call fails."""
    # Create a mock repository that raises an exception
    repo = MagicMock()
    type(repo).allow_auto_merge = PropertyMock(
        side_effect=GithubException(404, "Not found")
    )
    context = RuleContext(repository=repo)

    # Check the rule
    rule = AutoMergeDisabledRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "error" in result.message.lower()
    assert "not found" in result.message.lower()
    assert not result.fix_available
    assert result.fix_description is None


def test_auto_merge_disabled_rule_fix_success():
    """Test AutoMergeDisabledRule fix method when successful."""
    # Create a mock repository
    repo = MagicMock()
    context = RuleContext(repository=repo)

    # Fix the rule
    rule = AutoMergeDisabledRule()
    success, message = rule.fix(context)

    assert success is True
    assert "disabled" in message.lower()
    repo.edit.assert_called_once_with(allow_auto_merge=False)


def test_auto_merge_disabled_rule_fix_error():
    """Test AutoMergeDisabledRule fix method when GitHub API call fails."""
    # Create a mock repository that raises an exception
    repo = MagicMock()
    repo.edit.side_effect = GithubException(404, "Not found")
    context = RuleContext(repository=repo)

    # Fix the rule
    rule = AutoMergeDisabledRule()
    success, message = rule.fix(context)

    assert success is False
    assert "failed" in message.lower()
    assert "not found" in message.lower()
    repo.edit.assert_called_once_with(allow_auto_merge=False)
