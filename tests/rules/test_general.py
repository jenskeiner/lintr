"""Tests for archive rules."""

from unittest.mock import MagicMock, PropertyMock

from github.GithubException import GithubException

from repolint.rules.base import RuleResult
from repolint.rules.context import RuleContext
from repolint.rules.general import PreserveRepositoryRule
from repolint.rules.general import DiscussionsDisabledRule
from repolint.rules.general import ProjectsDisabledRule


def test_preserve_repository_rule_pass():
    """Test PreserveRepositoryRule passes when repository is archived."""
    # Create mock repository with archived=True
    mock_repo = MagicMock()
    mock_repo.archived = True

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = PreserveRepositoryRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.PASSED
    assert "preserved" in result.message.lower()


def test_preserve_repository_rule_fail():
    """Test PreserveRepositoryRule fails when repository is not archived."""
    # Create mock repository with archived=False
    mock_repo = MagicMock()
    mock_repo.archived = False

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = PreserveRepositoryRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "not preserved" in result.message.lower()
    assert result.fix_available
    assert "preserve" in result.fix_description.lower()


def test_preserve_repository_rule_fix():
    """Test PreserveRepositoryRule fix functionality."""
    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.archived = False

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run fix
    rule = PreserveRepositoryRule()
    success, message = rule.fix(context)

    # Verify fix was called with correct parameters
    mock_repo.edit.assert_called_once_with(archived=True)
    assert success
    assert "successfully" in message.lower()


def test_preserve_repository_rule_fix_dry_run():
    """Test PreserveRepositoryRule fix in dry run mode."""
    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.archived = False

    # Create context with mock repository in dry run mode
    context = RuleContext(mock_repo, dry_run=True)

    # Run fix
    rule = PreserveRepositoryRule()
    success, message = rule.fix(context)

    # Verify fix was not actually called
    mock_repo.edit.assert_not_called()
    assert success
    assert "would" in message.lower()


def test_preserve_repository_rule_api_error():
    """Test PreserveRepositoryRule when API call fails."""
    # Create mock repository that raises an exception
    mock_repo = MagicMock()
    type(mock_repo).archived = PropertyMock(
        side_effect=GithubException(500, "API Error")
    )

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = PreserveRepositoryRule()
    result = rule.check(context)

    # Verify error handling
    assert result.result == RuleResult.SKIPPED
    assert "failed" in result.message.lower()
    assert "api error" in result.message.lower()


def test_preserve_repository_rule_fix_api_error():
    """Test PreserveRepositoryRule fix when API call fails."""
    # Create mock repository that raises an exception on edit
    mock_repo = MagicMock()
    mock_repo.archived = False
    mock_repo.edit.side_effect = GithubException(500, "API Error")

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run fix
    rule = PreserveRepositoryRule()
    success, message = rule.fix(context)

    # Verify error handling
    assert not success
    assert "failed" in message.lower()
    assert "api error" in message.lower()


def test_discussions_disabled_rule_pass():
    """Test DiscussionsDisabledRule passes when discussions are disabled."""
    # Create mock repository with has_discussions=False
    mock_repo = MagicMock()
    mock_repo.has_discussions = False

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = DiscussionsDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.PASSED
    assert "disabled" in result.message.lower()


def test_discussions_disabled_rule_fail():
    """Test DiscussionsDisabledRule fails when discussions are enabled."""
    # Create mock repository with has_discussions=True
    mock_repo = MagicMock()
    mock_repo.has_discussions = True

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = DiscussionsDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "enabled" in result.message.lower()
    assert result.fix_available
    assert "disable" in result.fix_description.lower()


def test_discussions_disabled_rule_fix():
    """Test DiscussionsDisabledRule fix functionality."""
    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.has_discussions = True

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run fix
    rule = DiscussionsDisabledRule()
    success, message = rule.fix(context)

    # Verify fix was called with correct parameters
    mock_repo.edit.assert_called_once_with(has_discussions=False)
    assert success
    assert "successfully" in message.lower()


def test_discussions_disabled_rule_fix_dry_run():
    """Test DiscussionsDisabledRule fix in dry run mode."""
    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.has_discussions = True

    # Create context with mock repository in dry run mode
    context = RuleContext(mock_repo, dry_run=True)

    # Run fix
    rule = DiscussionsDisabledRule()
    success, message = rule.fix(context)

    # Verify fix was not actually called
    mock_repo.edit.assert_not_called()
    assert success
    assert "would" in message.lower()


def test_discussions_disabled_rule_api_error():
    """Test DiscussionsDisabledRule when API call fails."""
    # Create mock repository that raises an exception
    mock_repo = MagicMock()
    type(mock_repo).has_discussions = PropertyMock(
        side_effect=GithubException(500, "API Error")
    )

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = DiscussionsDisabledRule()
    result = rule.check(context)

    # Verify error handling
    assert result.result == RuleResult.SKIPPED
    assert "failed" in result.message.lower()
    assert "api error" in result.message.lower()


def test_discussions_disabled_rule_fix_api_error():
    """Test DiscussionsDisabledRule fix when API call fails."""
    # Create mock repository that raises an exception on edit
    mock_repo = MagicMock()
    mock_repo.has_discussions = True
    mock_repo.edit.side_effect = GithubException(500, "API Error")

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run fix
    rule = DiscussionsDisabledRule()
    success, message = rule.fix(context)

    # Verify error handling
    assert not success
    assert "failed" in message.lower()
    assert "api error" in message.lower()


def test_projects_disabled_rule_pass():
    """Test ProjectsDisabledRule passes when projects are disabled."""
    # Create mock repository with has_projects=False
    mock_repo = MagicMock()
    mock_repo.has_projects = False

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = ProjectsDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.PASSED
    assert "disabled" in result.message.lower()


def test_projects_disabled_rule_fail():
    """Test ProjectsDisabledRule fails when projects are enabled."""
    # Create mock repository with has_projects=True
    mock_repo = MagicMock()
    mock_repo.has_projects = True

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = ProjectsDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "enabled" in result.message.lower()
    assert result.fix_available
    assert "disable" in result.fix_description.lower()


def test_projects_disabled_rule_fix():
    """Test ProjectsDisabledRule fix functionality."""
    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.has_projects = True

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run fix
    rule = ProjectsDisabledRule()
    success, message = rule.fix(context)

    # Verify fix was called with correct parameters
    mock_repo.edit.assert_called_once_with(has_projects=False)
    assert success
    assert "successfully" in message.lower()


def test_projects_disabled_rule_fix_dry_run():
    """Test ProjectsDisabledRule fix in dry run mode."""
    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.has_projects = True

    # Create context with mock repository in dry run mode
    context = RuleContext(mock_repo, dry_run=True)

    # Run fix
    rule = ProjectsDisabledRule()
    success, message = rule.fix(context)

    # Verify fix was not actually called
    mock_repo.edit.assert_not_called()
    assert success
    assert "would" in message.lower()


def test_projects_disabled_rule_api_error():
    """Test ProjectsDisabledRule when API call fails."""
    # Create mock repository that raises an exception
    mock_repo = MagicMock()
    type(mock_repo).has_projects = PropertyMock(
        side_effect=GithubException(500, "API Error")
    )

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = ProjectsDisabledRule()
    result = rule.check(context)

    # Verify error handling
    assert result.result == RuleResult.SKIPPED
    assert "failed" in result.message.lower()
    assert "api error" in result.message.lower()


def test_projects_disabled_rule_fix_api_error():
    """Test ProjectsDisabledRule fix when API call fails."""
    # Create mock repository that raises an exception on edit
    mock_repo = MagicMock()
    mock_repo.has_projects = True
    mock_repo.edit.side_effect = GithubException(500, "API Error")

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run fix
    rule = ProjectsDisabledRule()
    success, message = rule.fix(context)

    # Verify error handling
    assert not success
    assert "failed" in message.lower()
    assert "api error" in message.lower()
