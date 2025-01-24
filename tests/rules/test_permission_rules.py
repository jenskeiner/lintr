"""Tests for permission rules."""

from unittest.mock import MagicMock

from github.GithubException import GithubException

from repolint.rules.base import RuleResult
from repolint.rules.context import RuleContext
from repolint.rules.permission_rules import SingleOwnerRule


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
        status=500,
        data={"message": "API Error"}
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
