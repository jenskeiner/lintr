"""Tests for permission rules."""

import pytest
from github.GithubException import GithubException
from unittest.mock import MagicMock, PropertyMock

from repolint.rules.base import RuleResult
from repolint.rules.context import RuleContext
from repolint.rules.permission_rules import (
    SingleOwnerRule,
    NoCollaboratorsRule,
    WikisDisabledRule,
    IssuesDisabledRule,
    MergeCommitsAllowedRule,
    SquashMergeDisabledRule,
    RebaseMergeDisabledRule,
    NoClassicBranchProtectionRule,
    DevelopBranchRulesetRule,
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


def test_merge_commits_allowed_rule_pass():
    """Test MergeCommitsAllowedRule when merge commits are allowed."""
    # Create mock repository
    mock_repo = MagicMock()
    type(mock_repo).allow_merge_commit = PropertyMock(return_value=True)

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = MergeCommitsAllowedRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.PASSED
    assert "Merge commits are allowed" in result.message


def test_merge_commits_allowed_rule_fail():
    """Test MergeCommitsAllowedRule when merge commits are not allowed."""
    # Create mock repository
    mock_repo = MagicMock()
    type(mock_repo).allow_merge_commit = PropertyMock(return_value=False)

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = MergeCommitsAllowedRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "Merge commits are not allowed" in result.message
    assert result.fix_available
    assert "Enable merge commits" in result.fix_description


def test_merge_commits_allowed_rule_fix():
    """Test MergeCommitsAllowedRule fix functionality."""
    # Create mock repository
    mock_repo = MagicMock()
    type(mock_repo).allow_merge_commit = PropertyMock(return_value=False)
    mock_repo.edit = MagicMock()

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run fix
    rule = MergeCommitsAllowedRule()
    success, message = rule.fix(context)

    # Verify fix
    assert success
    assert "Enabled merge commits" in message
    mock_repo.edit.assert_called_once_with(allow_merge_commit=True)


def test_merge_commits_allowed_rule_api_error():
    """Test MergeCommitsAllowedRule when API call fails."""
    # Create mock repository that raises an exception
    mock_repo = MagicMock()
    type(mock_repo).allow_merge_commit = PropertyMock(
        side_effect=GithubException(status=500, data={"message": "API Error"})
    )

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = MergeCommitsAllowedRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "API Error" in result.message
    assert not result.fix_available


def test_squash_merge_disabled_rule_pass():
    """Test SquashMergeDisabledRule when squash merging is disabled."""
    # Create mock repository
    mock_repo = MagicMock()
    type(mock_repo).allow_squash_merge = PropertyMock(return_value=False)

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = SquashMergeDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.PASSED
    assert "Squash merging is disabled" in result.message


def test_squash_merge_disabled_rule_fail():
    """Test SquashMergeDisabledRule when squash merging is enabled."""
    # Create mock repository
    mock_repo = MagicMock()
    type(mock_repo).allow_squash_merge = PropertyMock(return_value=True)

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = SquashMergeDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "Squash merging is enabled" in result.message
    assert result.fix_available
    assert "Disable squash merging" in result.fix_description


def test_squash_merge_disabled_rule_fix():
    """Test SquashMergeDisabledRule fix functionality."""
    # Create mock repository
    mock_repo = MagicMock()
    type(mock_repo).allow_squash_merge = PropertyMock(return_value=True)
    mock_repo.edit = MagicMock()

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run fix
    rule = SquashMergeDisabledRule()
    success, message = rule.fix(context)

    # Verify fix
    assert success
    assert "Disabled squash merging" in message
    mock_repo.edit.assert_called_once_with(allow_squash_merge=False)


def test_squash_merge_disabled_rule_api_error():
    """Test SquashMergeDisabledRule when API call fails."""
    # Create mock repository that raises an exception
    mock_repo = MagicMock()
    type(mock_repo).allow_squash_merge = PropertyMock(
        side_effect=GithubException(status=500, data={"message": "API Error"})
    )

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = SquashMergeDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "API Error" in result.message
    assert not result.fix_available


def test_rebase_merge_disabled_rule_pass():
    """Test RebaseMergeDisabledRule when rebase merging is disabled."""
    # Create mock repository
    mock_repo = MagicMock()
    type(mock_repo).allow_rebase_merge = PropertyMock(return_value=False)

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = RebaseMergeDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.PASSED
    assert "Rebase merging is disabled" in result.message


def test_rebase_merge_disabled_rule_fail():
    """Test RebaseMergeDisabledRule when rebase merging is enabled."""
    # Create mock repository
    mock_repo = MagicMock()
    type(mock_repo).allow_rebase_merge = PropertyMock(return_value=True)

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = RebaseMergeDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "Rebase merging is enabled" in result.message
    assert result.fix_available
    assert "Disable rebase merging" in result.fix_description


def test_rebase_merge_disabled_rule_fix():
    """Test RebaseMergeDisabledRule fix functionality."""
    # Create mock repository
    mock_repo = MagicMock()
    type(mock_repo).allow_rebase_merge = PropertyMock(return_value=True)
    mock_repo.edit = MagicMock()

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run fix
    rule = RebaseMergeDisabledRule()
    success, message = rule.fix(context)

    # Verify fix
    assert success
    assert "Disabled rebase merging" in message
    mock_repo.edit.assert_called_once_with(allow_rebase_merge=False)


def test_rebase_merge_disabled_rule_api_error():
    """Test RebaseMergeDisabledRule when API call fails."""
    # Create mock repository that raises an exception
    mock_repo = MagicMock()
    type(mock_repo).allow_rebase_merge = PropertyMock(
        side_effect=GithubException(status=500, data={"message": "API Error"})
    )

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = RebaseMergeDisabledRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "API Error" in result.message
    assert not result.fix_available


def test_no_classic_branch_protection_rule_pass():
    """Test NoClassicBranchProtectionRule when no classic branch protection is used."""
    # Create mock branch without protection
    mock_branch = MagicMock()
    mock_branch.name = "main"
    mock_branch.protected = False

    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.get_branches.return_value = [mock_branch]

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = NoClassicBranchProtectionRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.PASSED
    assert "No classic branch protection rules found" in result.message


def test_no_classic_branch_protection_rule_fail():
    """Test NoClassicBranchProtectionRule when classic branch protection is used."""
    # Create mock branch with classic protection
    mock_branch = MagicMock()
    mock_branch.name = "main"
    mock_branch.protected = True
    mock_protection = MagicMock()
    # Classic protection has no required_status_checks or required_pull_request_reviews
    mock_protection.required_status_checks = None
    mock_protection.required_pull_request_reviews = None
    mock_branch.get_protection.return_value = mock_protection

    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.get_branches.return_value = [mock_branch]

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = NoClassicBranchProtectionRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "main" in result.message
    assert result.fix_available


def test_no_classic_branch_protection_rule_fix():
    """Test NoClassicBranchProtectionRule fix functionality."""
    # Create mock branch with classic protection
    mock_branch = MagicMock()
    mock_branch.name = "main"
    mock_branch.protected = True
    mock_protection = MagicMock()
    # Classic protection has no required_status_checks or required_pull_request_reviews
    mock_protection.required_status_checks = None
    mock_protection.required_pull_request_reviews = None
    mock_branch.get_protection.return_value = mock_protection

    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.get_branches.return_value = [mock_branch]

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run fix
    rule = NoClassicBranchProtectionRule()
    success, message = rule.fix(context)

    # Verify result
    assert success
    assert "main" in message
    mock_branch.remove_protection.assert_called_once()


def test_no_classic_branch_protection_rule_api_error():
    """Test NoClassicBranchProtectionRule when API call fails."""
    # Create mock repository that raises an exception
    mock_repo = MagicMock()
    mock_repo.get_branches.side_effect = GithubException(500, "API Error")

    # Create context with mock repository
    context = RuleContext(mock_repo)

    # Run check
    rule = NoClassicBranchProtectionRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "Failed to check branch protection rules" in result.message
    assert not result.fix_available


def test_develop_branch_ruleset_rule_pass(mock_repository):
    """Test DevelopBranchRulesetRule when develop branch has proper ruleset."""
    # Create mock ruleset with all required rules
    mock_rules = []
    for rule_type in [
        "creation",
        "update",
        "deletion",
        "required_signatures",
        "pull_request",
        "non_fast_forward",
    ]:
        mock_rule = MagicMock()
        mock_rule.type = rule_type
        if rule_type == "pull_request":
            mock_rule.parameters = {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews_on_push": True,
                "require_code_owner_review": True,
                "require_last_push_approval": True,
                "required_review_thread_resolution": True,
                "automatic_copilot_code_review_enabled": False,
                "allowed_merge_methods": ["merge"],
            }
        else:
            mock_rule.parameters = None
        mock_rules.append(mock_rule)

    mock_ruleset = MagicMock()
    mock_ruleset.name = "develop protection"
    mock_ruleset.enforcement = "active"
    mock_ruleset.conditions = {
        "ref_name": {"include": ["refs/heads/develop"], "exclude": []}
    }
    mock_ruleset.rules = mock_rules

    # Create mock repository
    mock_repository.get_rulesets.return_value = [mock_ruleset]

    # Create context with mock repository
    context = RuleContext(mock_repository)

    # Run check
    rule = DevelopBranchRulesetRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.PASSED
    assert "Ruleset 'develop protection' properly configured" in result.message
    assert not result.fix_available


def test_develop_branch_ruleset_rule_fail_missing_rules(mock_repository):
    """Test DevelopBranchRulesetRule when ruleset is missing required rules."""
    # Create mock ruleset with missing rules
    mock_rules = []
    # Only add some of the required rules
    for rule_type in ["creation", "update"]:
        mock_rule = MagicMock()
        mock_rule.type = rule_type
        mock_rule.parameters = {"enabled": True}
        mock_rules.append(mock_rule)

    mock_ruleset = MagicMock()
    mock_ruleset.name = "develop protection"
    mock_ruleset.enforcement = "active"
    mock_ruleset.conditions = {
        "ref_name": {"include": ["refs/heads/develop"], "exclude": []}
    }
    mock_ruleset.rules = mock_rules

    # Create mock repository
    mock_repository.get_rulesets.return_value = [mock_ruleset]

    # Create context with mock repository
    context = RuleContext(mock_repository)

    # Run check
    rule = DevelopBranchRulesetRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "Missing rule: restrict deletion" in result.message
    assert "Missing rule: require signed commits" in result.message
    assert "Missing rule: require pull request before merging" in result.message
    assert "Missing rule: block force pushes" in result.message
    assert result.fix_available


def test_develop_branch_ruleset_rule_fail_no_ruleset(mock_repository):
    """Test DevelopBranchRulesetRule when no develop branch ruleset exists."""
    # Create mock repository with no rulesets
    mock_repository.get_rulesets.return_value = []

    # Create context with mock repository
    context = RuleContext(mock_repository)

    # Run check
    rule = DevelopBranchRulesetRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "No 'develop protection' ruleset found" in result.message
    assert result.fix_available
    assert "Create a ruleset for the develop branch" in result.fix_description


def test_develop_branch_ruleset_rule_fail_disabled(mock_repository):
    """Test DevelopBranchRulesetRule when ruleset exists but is disabled."""
    # Create mock ruleset that is disabled
    mock_ruleset = MagicMock()
    mock_ruleset.name = "develop protection"
    mock_ruleset.enforcement = "disabled"
    mock_ruleset.conditions = {
        "ref_name": {"include": ["refs/heads/develop"], "exclude": []}
    }

    # Create mock repository
    mock_repository.get_rulesets.return_value = [mock_ruleset]

    # Create context with mock repository
    context = RuleContext(mock_repository)

    # Run check
    rule = DevelopBranchRulesetRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "Ruleset must be enabled" in result.message
    assert result.fix_available
    assert "Update ruleset configuration" in result.fix_description


def test_develop_branch_ruleset_rule_fail_wrong_branch(mock_repository):
    """Test DevelopBranchRulesetRule when ruleset doesn't target develop branch."""
    # Create mock ruleset that targets wrong branch
    mock_ruleset = MagicMock()
    mock_ruleset.name = "develop protection"
    mock_ruleset.enforcement = "active"
    mock_ruleset.conditions = {
        "ref_name": {"include": ["refs/heads/main"], "exclude": []}
    }

    # Create mock repository
    mock_repository.get_rulesets.return_value = [mock_ruleset]

    # Create context with mock repository
    context = RuleContext(mock_repository)

    # Run check
    rule = DevelopBranchRulesetRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "Ruleset must apply to the develop branch" in result.message
    assert result.fix_available
    assert "Update ruleset configuration" in result.fix_description


def test_develop_branch_ruleset_rule_multiple_rulesets(mock_repository):
    """Test DevelopBranchRulesetRule when multiple rulesets exist."""
    # Create mock rulesets
    mock_ruleset1 = MagicMock()
    mock_ruleset1.name = "main protection"
    mock_ruleset1.enforcement = "active"

    # Create mock rules for develop ruleset
    mock_rules = []
    for rule_type in [
        "creation",
        "update",
        "deletion",
        "required_signatures",
        "pull_request",
        "non_fast_forward",
    ]:
        mock_rule = MagicMock()
        mock_rule.type = rule_type
        if rule_type == "pull_request":
            mock_rule.parameters = {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews_on_push": True,
                "require_code_owner_review": True,
                "require_last_push_approval": True,
                "required_review_thread_resolution": True,
                "automatic_copilot_code_review_enabled": False,
                "allowed_merge_methods": ["merge"],
            }
        else:
            mock_rule.parameters = None
        mock_rules.append(mock_rule)

    mock_ruleset2 = MagicMock()
    mock_ruleset2.name = "develop protection"
    mock_ruleset2.enforcement = "active"
    mock_ruleset2.conditions = {
        "ref_name": {"include": ["refs/heads/develop"], "exclude": []}
    }
    mock_ruleset2.rules = mock_rules

    # Create mock repository
    mock_repository.get_rulesets.return_value = [mock_ruleset1, mock_ruleset2]

    # Create context with mock repository
    context = RuleContext(mock_repository)

    # Run check
    rule = DevelopBranchRulesetRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.PASSED
    assert "Ruleset 'develop protection' properly configured" in result.message
    assert not result.fix_available


def test_develop_branch_ruleset_rule_api_error(mock_repository):
    """Test DevelopBranchRulesetRule when API call fails."""
    # Mock API error
    mock_repository.get_rulesets.side_effect = GithubException(
        status=404, data={"message": "Repository rulesets not found"}
    )

    # Create context with mock repository
    context = RuleContext(mock_repository)

    # Run check
    rule = DevelopBranchRulesetRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "Repository rulesets not found" in result.message
    assert result.fix_available
    assert "Create a ruleset for the develop branch" in result.fix_description


def test_develop_branch_ruleset_rule_other_api_error(mock_repository):
    """Test DevelopBranchRulesetRule when API call fails with unexpected error."""
    # Mock unexpected API error
    mock_repository.get_rulesets.side_effect = GithubException(
        status=500, data={"message": "Internal server error"}
    )

    # Create context with mock repository
    context = RuleContext(mock_repository)

    # Run check
    rule = DevelopBranchRulesetRule()

    # Verify that other API errors are re-raised
    with pytest.raises(GithubException):
        rule.check(context)


def test_develop_branch_ruleset_rule_fail_additional_rules(mock_repository):
    """Test DevelopBranchRulesetRule when ruleset has additional rules that are not allowed."""
    # Create mock ruleset with required and additional rules
    mock_rules = []
    # Add required rules
    for rule_type in [
        "creation",
        "update",
        "deletion",
        "required_signatures",
        "required_pull_request",
        "non_fast_forward",
    ]:
        mock_rule = MagicMock()
        mock_rule.type = rule_type
        mock_rule.parameters = {"enabled": True}
        mock_rules.append(mock_rule)

    # Add additional rules that are not allowed
    for rule_type in ["required_linear_history", "required_deployments"]:
        mock_rule = MagicMock()
        mock_rule.type = rule_type
        mock_rule.parameters = {"enabled": True}
        mock_rules.append(mock_rule)

    mock_ruleset = MagicMock()
    mock_ruleset.name = "develop protection"
    mock_ruleset.enforcement = "active"
    mock_ruleset.conditions = {
        "ref_name": {"include": ["refs/heads/develop"], "exclude": []}
    }
    mock_ruleset.rules = mock_rules

    # Create mock repository
    mock_repository.get_rulesets.return_value = [mock_ruleset]

    # Create context with mock repository
    context = RuleContext(mock_repository)

    # Run check
    rule = DevelopBranchRulesetRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert (
        "Additional rules found that are not allowed: required_deployments, required_linear_history"
        in result.message
    )
    assert result.fix_available
    assert (
        "Update ruleset configuration for the develop branch" == result.fix_description
    )


def test_develop_branch_ruleset_rule_fail_multiple_branches(mock_repository):
    """Test DevelopBranchRulesetRule when ruleset applies to multiple branches."""
    # Create mock ruleset with all required rules
    mock_rules = []
    for rule_type in [
        "creation",
        "update",
        "deletion",
        "required_signatures",
        "required_pull_request",
        "non_fast_forward",
    ]:
        mock_rule = MagicMock()
        mock_rule.type = rule_type
        mock_rule.parameters = {"enabled": True}
        mock_rules.append(mock_rule)

    mock_ruleset = MagicMock()
    mock_ruleset.name = "develop protection"
    mock_ruleset.enforcement = "active"
    mock_ruleset.conditions = {
        "ref_name": {
            "include": [
                "refs/heads/develop",
                "refs/heads/main",
                "refs/heads/feature/*",
            ],
            "exclude": [],
        }
    }
    mock_ruleset.rules = mock_rules

    # Create mock repository
    mock_repository.get_rulesets.return_value = [mock_ruleset]

    # Create context with mock repository
    context = RuleContext(mock_repository)

    # Run check
    rule = DevelopBranchRulesetRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert (
        "Ruleset must only apply to develop branch, but also includes: refs/heads/feature/*, refs/heads/main"
        in result.message
    )
    assert result.fix_available


def test_develop_branch_ruleset_rule_fail_excluded_branches(mock_repository):
    """Test DevelopBranchRulesetRule when ruleset has excluded branches."""
    # Create mock ruleset with all required rules
    mock_rules = []
    for rule_type in [
        "creation",
        "update",
        "deletion",
        "required_signatures",
        "pull_request",
        "non_fast_forward",
    ]:
        mock_rule = MagicMock()
        mock_rule.type = rule_type
        if rule_type == "pull_request":
            mock_rule.parameters = {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews_on_push": True,
                "require_code_owner_review": True,
                "require_last_push_approval": True,
                "required_review_thread_resolution": True,
                "automatic_copilot_code_review_enabled": False,
                "allowed_merge_methods": ["merge"],
            }
        else:
            mock_rule.parameters = None
        mock_rules.append(mock_rule)

    mock_ruleset = MagicMock()
    mock_ruleset.name = "develop protection"
    mock_ruleset.enforcement = "active"
    mock_ruleset.conditions = {
        "ref_name": {
            "include": ["refs/heads/develop"],
            "exclude": ["refs/heads/feature/*", "refs/heads/hotfix/*"],
        }
    }
    mock_ruleset.rules = mock_rules

    # Create mock repository
    mock_repository.get_rulesets.return_value = [mock_ruleset]

    # Create context with mock repository
    context = RuleContext(mock_repository)

    # Run check
    rule = DevelopBranchRulesetRule()
    result = rule.check(context)

    # Verify result
    assert result.result == RuleResult.FAILED
    assert "Rulesset 'develop protection' not set up correctly:" in result.message
    assert (
        "Ruleset must not exclude any branches, but excludes: refs/heads/feature/*, refs/heads/hotfix/*"
        in result.message
    )
    assert result.fix_available


def test_develop_branch_ruleset_rule_fix_create(mock_repository):
    """Test DevelopBranchRulesetRule fix when no ruleset exists."""
    # Mock that no rulesets exist
    mock_repository.get_rulesets.return_value = []

    # Create context with mock repository
    context = RuleContext(mock_repository)

    # Run fix
    rule = DevelopBranchRulesetRule()
    success, message = rule.fix(context)

    # Verify result
    assert success
    assert "Created new develop branch ruleset" in message

    # Verify that create_ruleset was called with correct arguments
    mock_repository.create_ruleset.assert_called_once()
    call_args = mock_repository.create_ruleset.call_args[1]
    assert call_args["name"] == "develop protection"
    assert call_args["target"] == "branch"
    assert call_args["enforcement"] == "active"
    assert call_args["conditions"]["ref_name"]["include"] == ["refs/heads/develop"]
    assert call_args["conditions"]["ref_name"]["exclude"] == []

    # Check rules
    rules = call_args["rules"]
    assert len(rules) == 6
    rule_types = {rule["type"] for rule in rules}
    assert rule_types == {
        "creation",
        "update",
        "deletion",
        "required_signatures",
        "pull_request",
        "non_fast_forward",
    }


def test_develop_branch_ruleset_rule_fix_update(mock_repository):
    """Test DevelopBranchRulesetRule fix when ruleset exists."""
    # Create mock existing ruleset
    mock_ruleset = MagicMock()
    mock_ruleset.name = "develop protection"
    mock_repository.get_rulesets.return_value = [mock_ruleset]

    # Create context with mock repository
    context = RuleContext(mock_repository)

    # Run fix
    rule = DevelopBranchRulesetRule()
    success, message = rule.fix(context)

    # Verify result
    assert success
    assert "Updated existing develop branch ruleset" in message

    # Verify that update was called with correct arguments
    mock_ruleset.update.assert_called_once()
    call_args = mock_ruleset.update.call_args[1]
    assert call_args["name"] == "develop protection"
    assert call_args["target"] == "branch"
    assert call_args["enforcement"] == "active"
    assert call_args["conditions"]["ref_name"]["include"] == ["refs/heads/develop"]
    assert call_args["conditions"]["ref_name"]["exclude"] == []

    # Check rules
    rules = call_args["rules"]
    assert len(rules) == 6
    rule_types = {rule["type"] for rule in rules}
    assert rule_types == {
        "creation",
        "update",
        "deletion",
        "required_signatures",
        "pull_request",
        "non_fast_forward",
    }


def test_develop_branch_ruleset_rule_fix_error(mock_repository):
    """Test DevelopBranchRulesetRule fix when API call fails."""
    # Mock API error
    mock_repository.get_rulesets.side_effect = GithubException(
        status=500, data={"message": "Internal server error"}
    )

    # Create context with mock repository
    context = RuleContext(mock_repository)

    # Run fix
    rule = DevelopBranchRulesetRule()
    success, message = rule.fix(context)

    # Verify result
    assert not success
    assert "Failed to fix branch ruleset:" in message
    assert "Internal server error" in message
