"""Tests for permission rules."""

from unittest.mock import MagicMock, PropertyMock

from github.GithubException import GithubException

from repolint.rules.base import RuleResult
from repolint.rules.context import RuleContext
from repolint.rules.permission_rules import (
    SingleOwnerRule,
    NoCollaboratorsRule,
    WikisDisabledRule,
    IssuesDisabledRule,
)


def test_single_owner_rule_pass():
    """Test SingleOwnerRule passes when user is the only admin."""
    # Create mock collaborator with admin permissions
    mock_collaborator = MagicMock()
    mock_collaborator.login = "test-user"
    mock_collaborator.permissions.admin = True

    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.get_collaborators.return_value = [mock_collaborator]
    mock_repo.owner.login = "test-user"

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = SingleOwnerRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.PASSED
    assert "test-user" in result.message


def test_single_owner_rule_fail_multiple_admins():
    """Test SingleOwnerRule fails when there are multiple admins."""
    # Create mock collaborators with admin permissions
    mock_collaborator1 = MagicMock()
    mock_collaborator1.login = "test-user"
    mock_collaborator1.permissions.admin = True

    mock_collaborator2 = MagicMock()
    mock_collaborator2.login = "other-admin"
    mock_collaborator2.permissions.admin = True

    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.get_collaborators.return_value = [mock_collaborator1, mock_collaborator2]
    mock_repo.owner.login = "test-user"

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = SingleOwnerRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "other-admin" in result.message
    assert not result.fix_available


def test_single_owner_rule_fail_api_error():
    """Test SingleOwnerRule fails gracefully on API error."""
    # Create mock repository that raises an exception
    mock_repo = MagicMock()
    mock_repo.get_collaborators.side_effect = GithubException(
        status=500, data={"message": "API Error"}
    )

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = SingleOwnerRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "API Error" in result.message
    assert not result.fix_available


def test_no_collaborators_rule_pass(mock_repository, config):
    """Test NoCollaboratorsRule when repository has no collaborators."""
    # Create rule
    rule = NoCollaboratorsRule()

    # Mock collaborators
    mock_repository.get_collaborators.return_value = []
    mock_repository.owner.login = "test-user"

    # Create context
    context = RuleContext(mock_repository, config)

    # Run check
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.PASSED
    assert "no collaborators" in result.message
    assert not result.fix_available


def test_no_collaborators_rule_fail(mock_repository, config):
    """Test NoCollaboratorsRule when repository has other collaborators."""
    # Create rule
    rule = NoCollaboratorsRule()

    # Create mock collaborators
    class MockCollaborator:
        def __init__(self, login):
            self.login = login

    collaborators = [
        MockCollaborator("test-user"),  # The owner
        MockCollaborator("other-user"),  # Another collaborator
    ]

    # Mock repository
    mock_repository.get_collaborators.return_value = collaborators
    mock_repository.owner.login = "test-user"

    # Create context
    context = RuleContext(mock_repository, config)

    # Run check
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "other-user" in result.message
    assert result.fix_available
    assert "Remove collaborators" in result.fix_description


def test_no_collaborators_rule_fix(mock_repository, config):
    """Test NoCollaboratorsRule fix functionality."""
    # Create rule
    rule = NoCollaboratorsRule()

    # Create mock collaborators
    class MockCollaborator:
        def __init__(self, login):
            self.login = login

    collaborators = [
        MockCollaborator("test-user"),  # The owner
        MockCollaborator("other-user"),  # Another collaborator
    ]

    # Mock repository
    mock_repository.get_collaborators.return_value = collaborators
    mock_repository.owner.login = "test-user"
    mock_repository.remove_from_collaborators = MagicMock()

    # Create context
    context = RuleContext(mock_repository, config)

    # Run fix
    success, message = rule.fix(context)

    # Verify fix
    assert success
    assert "Removed collaborators" in message
    assert "other-user" in message
    mock_repository.remove_from_collaborators.assert_called_once_with("other-user")


def test_no_collaborators_rule_api_error(mock_repository, config):
    """Test NoCollaboratorsRule when API call fails."""
    # Create rule
    rule = NoCollaboratorsRule()

    # Mock API error
    mock_repository.get_collaborators.side_effect = Exception("API error")

    # Create context
    context = RuleContext(mock_repository, config)

    # Run check
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "Failed to check collaborators" in result.message
    assert not result.fix_available


def test_wikis_disabled_rule_pass():
    """Test WikisDisabledRule when wikis are disabled."""
    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.has_wiki = False

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = WikisDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.PASSED
    assert "disabled" in result.message


def test_wikis_disabled_rule_fail():
    """Test WikisDisabledRule when wikis are enabled."""
    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.has_wiki = True

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = WikisDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "enabled" in result.message
    assert result.fix_available
    assert "disable" in result.fix_description.lower()


def test_wikis_disabled_rule_fix():
    """Test WikisDisabledRule fix functionality."""
    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.has_wiki = True

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run fix
    rule = WikisDisabledRule()
    success, message = rule.fix(context)

    # Verify fix was called correctly
    mock_repo.edit.assert_called_once_with(has_wiki=False)
    assert success
    assert "disabled" in message.lower()


def test_wikis_disabled_rule_api_error():
    """Test WikisDisabledRule when API call fails."""
    # Create mock repository that raises an exception
    mock_repo = MagicMock()
    type(mock_repo).has_wiki = PropertyMock(
        side_effect=GithubException(500, "API Error")
    )

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = WikisDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "Failed to check" in result.message
    assert "API Error" in result.message


def test_issues_disabled_rule_pass():
    """Test IssuesDisabledRule when issues are disabled."""
    # Create mock repository
    mock_repo = MagicMock()
    type(mock_repo).has_issues = PropertyMock(return_value=False)

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = IssuesDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.PASSED
    assert "disabled" in result.message


def test_issues_disabled_rule_fail():
    """Test IssuesDisabledRule when issues are enabled."""
    # Create mock repository
    mock_repo = MagicMock()
    type(mock_repo).has_issues = PropertyMock(return_value=True)

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = IssuesDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "enabled" in result.message
    assert result.fix_available
    assert "disable" in result.fix_description.lower()


def test_issues_disabled_rule_fix():
    """Test IssuesDisabledRule fix functionality."""
    # Create mock repository
    mock_repo = MagicMock()
    type(mock_repo).has_issues = PropertyMock(return_value=True)

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run fix
    rule = IssuesDisabledRule()
    success, message = rule.fix(context)

    # Verify fix was called correctly
    mock_repo.edit.assert_called_once_with(has_issues=False)
    assert success
    assert "disabled" in message.lower()


def test_issues_disabled_rule_api_error():
    """Test IssuesDisabledRule when API call fails."""
    # Create mock repository that raises an exception
    mock_repo = MagicMock()
    type(mock_repo).has_issues = PropertyMock(
        side_effect=GithubException(500, "API Error")
    )

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = IssuesDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "Failed to check" in result.message
    assert "API Error" in result.message
