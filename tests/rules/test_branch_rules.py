"""Tests for branch-related rules."""

from unittest.mock import MagicMock, PropertyMock
from github.GithubException import GithubException

from lintr.rules.base import RuleResult
from lintr.rules.general import (
    WebCommitSignoffRequiredEnabledRule,
    AutoMergeDisabledRule,
    DeleteBranchOnMergeEnabledRule,
)
from lintr.rules.context import RuleContext


def test_web_commit_signoff_required_rule_init():
    """Test initialization of WebCommitSignoffRequiredRule."""
    rule = WebCommitSignoffRequiredEnabledRule()
    assert rule.rule_id == "G001P"
    assert "web-based commits" in rule.description.lower()


def test_web_commit_signoff_required_rule_check_success():
    """Test WebCommitSignoffRequiredRule when signoff is required."""
    # Create a mock repository with web commit signoff required
    repo = MagicMock()
    repo.web_commit_signoff_required = True
    context = RuleContext(repository=repo)

    # Check the rule
    rule = WebCommitSignoffRequiredEnabledRule()
    result = rule.check(context)

    assert result.result == RuleResult.PASSED
    assert (
        "require contributors to sign off on web-based commits"
        in result.message.lower()
    )
    assert not result.fix_available
    assert result.fix_description is None


def test_web_commit_signoff_required_rule_check_failure():
    """Test WebCommitSignoffRequiredRule when signoff is not required."""
    # Create a mock repository without web commit signoff required
    repo = MagicMock()
    repo.web_commit_signoff_required = False
    context = RuleContext(repository=repo)

    # Check the rule
    rule = WebCommitSignoffRequiredEnabledRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "is disabled" in result.message.lower()
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
    rule = WebCommitSignoffRequiredEnabledRule()
    result = rule.check(context)

    assert result.result == RuleResult.SKIPPED
    assert "failed to check" in result.message.lower()
    assert "not found" in result.message.lower()
    assert not result.fix_available
    assert result.fix_description is None


def test_web_commit_signoff_required_rule_fix_success():
    """Test WebCommitSignoffRequiredRule fix method when successful."""
    # Create a mock repository
    repo = MagicMock()
    context = RuleContext(repository=repo)

    # Fix the issue
    rule = WebCommitSignoffRequiredEnabledRule()
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
    rule = WebCommitSignoffRequiredEnabledRule()
    success, message = rule.fix(context)

    assert not success
    assert "failed to enable" in message.lower()
    assert "not found" in message.lower()
    repo.edit.assert_called_once_with(web_commit_signoff_required=True)


def test_delete_branch_on_merge_rule_init():
    """Test initialization of DeleteBranchOnMergeEnabledRule."""
    rule = DeleteBranchOnMergeEnabledRule()
    assert rule.rule_id == "G011P"
    assert "checks that automatically delete" in rule.description.lower()


def test_delete_branch_on_merge_rule_check_success():
    """Test DeleteBranchOnMergeEnabledRule when delete_branch_on_merge is enabled."""
    # Create a mock repository with delete_branch_on_merge enabled
    repo = MagicMock()
    repo.delete_branch_on_merge = True
    context = RuleContext(repository=repo)

    # Check the rule
    rule = DeleteBranchOnMergeEnabledRule()
    result = rule.check(context)

    assert result.result == RuleResult.PASSED
    assert "enabled" in result.message.lower()
    assert not result.fix_available
    assert result.fix_description is None


def test_delete_branch_on_merge_rule_check_failure():
    """Test DeleteBranchOnMergeEnabledRule when delete_branch_on_merge is disabled."""
    # Create a mock repository with delete_branch_on_merge disabled
    repo = MagicMock()
    repo.delete_branch_on_merge = False
    context = RuleContext(repository=repo)

    # Check the rule
    rule = DeleteBranchOnMergeEnabledRule()
    result = rule.check(context)

    assert result.result == RuleResult.FAILED
    assert "is disabled" in result.message.lower()
    assert result.fix_available
    assert "enable" in result.fix_description.lower()


def test_delete_branch_on_merge_rule_check_error():
    """Test DeleteBranchOnMergeEnabledRule when GitHub API call fails."""
    # Create a mock repository that raises an exception
    repo = MagicMock()
    type(repo).delete_branch_on_merge = PropertyMock(
        side_effect=GithubException(404, "Not found")
    )
    context = RuleContext(repository=repo)

    # Check the rule
    rule = DeleteBranchOnMergeEnabledRule()
    result = rule.check(context)

    assert result.result == RuleResult.SKIPPED
    assert "failed to check" in result.message.lower()
    assert "not found" in result.message.lower()
    assert not result.fix_available
    assert result.fix_description is None


def test_delete_branch_on_merge_rule_fix_success():
    """Test DeleteBranchOnMergeEnabledRule fix method when successful."""
    # Create a mock repository
    repo = MagicMock()
    context = RuleContext(repository=repo)

    # Fix the rule
    rule = DeleteBranchOnMergeEnabledRule()
    success, message = rule.fix(context)

    assert success is True
    assert "enabled" in message.lower()
    repo.edit.assert_called_once_with(delete_branch_on_merge=True)


def test_delete_branch_on_merge_rule_fix_error():
    """Test DeleteBranchOnMergeEnabledRule fix method when GitHub API call fails."""
    # Create a mock repository that raises an exception
    repo = MagicMock()
    repo.edit.side_effect = GithubException(404, "Not found")
    context = RuleContext(repository=repo)

    # Fix the rule
    rule = DeleteBranchOnMergeEnabledRule()
    success, message = rule.fix(context)

    assert success is False
    assert "failed" in message.lower()
    assert "not found" in message.lower()
    repo.edit.assert_called_once_with(delete_branch_on_merge=True)


def test_auto_merge_disabled_rule_init():
    """Test initialization of AutoMergeDisabledRule."""
    rule = AutoMergeDisabledRule()
    assert rule.rule_id == "G010N"
    assert "checks that 'allow auto-merge'" in rule.description.lower()


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

    assert result.result == RuleResult.SKIPPED
    assert "failed to check" in result.message.lower()
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
