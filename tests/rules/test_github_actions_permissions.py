# """Tests for the GitHub Actions permissions rule."""

# from unittest.mock import MagicMock

# from github.GithubException import GithubException

# from lintr.rules.permission_rules import (
#     GitHubActionsPermissionsRule,
#     GitHubActionsEnabledRule,
#     GitHubActionsDisabledRule,
#     GitHubActionsLocalOnlyRule,
#     ActionsPermissionsRuleConfig,
#     AllowedActionsEnum,
# )
# from lintr.rules.base import RuleResult
# from lintr.rules.context import RuleContext


# class TestGitHubActionsPermissionsRule:
#     """Tests for the GitHub Actions permissions rule."""

#     def setup_method(self):
#         """Set up test fixtures."""
#         self.repository = MagicMock()
#         self.repository.owner.login = "test-owner"
#         self.repository.name = "test-repo"
#         self.context = RuleContext(repository=self.repository)

#     def test_check_actions_enabled_success(self):
#         """Test checking GitHub Actions permissions when enabled and should be enabled."""
#         # Configure the mock repository
#         self.repository._requester.requestJsonAndCheck.return_value = [
#             {"enabled": True, "allowed_actions": "all"}
#         ]

#         # Create rule with config to check that actions are enabled
#         rule = GitHubActionsEnabledRule()

#         # Check the rule
#         result = rule.check(self.context)

#         # Verify the result
#         assert result.result == RuleResult.PASSED
#         assert "GitHub Actions permissions are correctly configured" in result.message
#         assert not result.fix_available

#         # Verify the API call
#         self.repository._requester.requestJsonAndCheck.assert_called_once_with(
#             "GET", "/repos/test-owner/test-repo/actions/permissions"
#         )

#     def test_check_actions_disabled_success(self):
#         """Test checking GitHub Actions permissions when disabled and should be disabled."""
#         # Configure the mock repository
#         self.repository._requester.requestJsonAndCheck.return_value = [
#             {"enabled": False, "allowed_actions": "all"}
#         ]

#         # Create rule with config to check that actions are disabled
#         rule = GitHubActionsDisabledRule()

#         # Check the rule
#         result = rule.check(self.context)

#         # Verify the result
#         assert result.result == RuleResult.PASSED
#         assert "GitHub Actions is correctly disabled" in result.message
#         assert not result.fix_available

#     def test_check_actions_enabled_but_should_be_disabled(self):
#         """Test checking GitHub Actions permissions when enabled but should be disabled."""
#         # Configure the mock repository
#         self.repository._requester.requestJsonAndCheck.return_value = [
#             {"enabled": True, "allowed_actions": "all"}
#         ]

#         # Create rule with config to check that actions are disabled
#         rule = GitHubActionsDisabledRule()

#         # Check the rule
#         result = rule.check(self.context)

#         # Verify the result
#         assert result.result == RuleResult.FAILED
#         assert "GitHub Actions is enabled but should be disabled" in result.message
#         assert result.fix_available
#         assert "Disable GitHub Actions" in result.fix_description

#     def test_check_actions_disabled_but_should_be_enabled(self):
#         """Test checking GitHub Actions permissions when disabled but should be enabled."""
#         # Configure the mock repository
#         self.repository._requester.requestJsonAndCheck.return_value = [
#             {"enabled": False, "allowed_actions": "all"}
#         ]

#         # Create rule with config to check that actions are enabled
#         rule = GitHubActionsEnabledRule()

#         # Check the rule
#         result = rule.check(self.context)

#         # Verify the result
#         assert result.result == RuleResult.FAILED
#         assert "GitHub Actions is disabled but should be enabled" in result.message
#         assert result.fix_available
#         assert "Enable GitHub Actions" in result.fix_description

#     def test_check_allowed_actions_mismatch(self):
#         """Test checking GitHub Actions permissions when allowed_actions doesn't match."""
#         # Configure the mock repository
#         self.repository._requester.requestJsonAndCheck.return_value = [
#             {"enabled": True, "allowed_actions": "all"}
#         ]

#         # Create rule with config to check that actions are local_only
#         rule = GitHubActionsLocalOnlyRule()

#         # Check the rule
#         result = rule.check(self.context)

#         # Verify the result
#         assert result.result == RuleResult.FAILED
#         assert "allowed_actions is set to 'all' but should be 'local_only'" in result.message
#         assert result.fix_available

#     def test_check_selected_actions_success(self):
#         """Test checking GitHub Actions permissions with selected actions configuration."""
#         # Configure the mock repository for permissions
#         self.repository._requester.requestJsonAndCheck.side_effect = [
#             [{"enabled": True, "allowed_actions": "selected"}],  # First call for permissions
#             [{"github_owned_allowed": True, "verified_allowed": True, "patterns_allowed": ["owner/repo"]}]  # Second call for selected actions
#         ]

#         # Create rule with config to check selected actions
#         rule = GitHubActionsPermissionsRule(
#             config=ActionsPermissionsRuleConfig(
#                 enabled=True,
#                 allowed_actions=AllowedActionsEnum.SELECTED,
#                 github_owned_allowed=True,
#                 verified_allowed=True,
#                 patterns_allowed=["owner/repo"]
#             )
#         )

#         # Check the rule
#         result = rule.check(self.context)

#         # Verify the result
#         assert result.result == RuleResult.PASSED
#         assert "GitHub Actions permissions are correctly configured" in result.message

#         # Verify the API calls
#         assert self.repository._requester.requestJsonAndCheck.call_count == 2
#         self.repository._requester.requestJsonAndCheck.assert_any_call(
#             "GET", "/repos/test-owner/test-repo/actions/permissions"
#         )
#         self.repository._requester.requestJsonAndCheck.assert_any_call(
#             "GET", "/repos/test-owner/test-repo/actions/permissions/selected-actions"
#         )

#     def test_check_selected_actions_mismatch(self):
#         """Test checking GitHub Actions permissions with mismatched selected actions configuration."""
#         # Configure the mock repository for permissions
#         self.repository._requester.requestJsonAndCheck.side_effect = [
#             [{"enabled": True, "allowed_actions": "selected"}],  # First call for permissions
#             [{"github_owned_allowed": True, "verified_allowed": False, "patterns_allowed": ["owner/repo"]}]  # Second call for selected actions
#         ]

#         # Create rule with config to check selected actions
#         rule = GitHubActionsPermissionsRule(
#             config=ActionsPermissionsRuleConfig(
#                 enabled=True,
#                 allowed_actions=AllowedActionsEnum.SELECTED,
#                 github_owned_allowed=True,
#                 verified_allowed=True,  # This doesn't match the actual setting
#                 patterns_allowed=["owner/repo"]
#             )
#         )

#         # Check the rule
#         result = rule.check(self.context)

#         # Verify the result
#         assert result.result == RuleResult.FAILED
#         assert "Verified actions are not allowed but should be allowed" in result.message
#         assert result.fix_available

#     def test_check_api_error(self):
#         """Test checking GitHub Actions permissions when API call fails."""
#         # Configure the mock repository to raise an exception
#         self.repository._requester.requestJsonAndCheck.side_effect = GithubException(
#             500, {"message": "API error"}
#         )

#         # Create rule
#         rule = GitHubActionsEnabledRule()

#         # Check the rule
#         result = rule.check(self.context)

#         # Verify the result
#         assert result.result == RuleResult.FAILED
#         assert "Failed to check GitHub Actions permissions" in result.message
#         assert not result.fix_available

#     def test_fix_enable_actions(self):
#         """Test fixing GitHub Actions permissions to enable actions."""
#         # Configure the mock repository
#         self.repository._requester.requestJsonAndCheck.return_value = [{}]

#         # Create rule with config to enable actions
#         rule = GitHubActionsEnabledRule()

#         # Apply the fix
#         success, message = rule.fix(self.context)

#         # Verify the result
#         assert success
#         assert "Updated GitHub Actions permissions successfully" in message

#         # Verify the API call
#         self.repository._requester.requestJsonAndCheck.assert_called_once_with(
#             "PUT",
#             "/repos/test-owner/test-repo/actions/permissions",
#             input={"enabled": True, "allowed_actions": "all"}
#         )

#     def test_fix_selected_actions(self):
#         """Test fixing GitHub Actions permissions with selected actions configuration."""
#         # Configure the mock repository
#         self.repository._requester.requestJsonAndCheck.return_value = [{}]

#         # Create rule with config for selected actions
#         rule = GitHubActionsPermissionsRule(
#             config=ActionsPermissionsRuleConfig(
#                 enabled=True,
#                 allowed_actions=AllowedActionsEnum.SELECTED,
#                 github_owned_allowed=True,
#                 verified_allowed=True,
#                 patterns_allowed=["owner/repo"]
#             )
#         )

#         # Apply the fix
#         success, message = rule.fix(self.context)

#         # Verify the result
#         assert success
#         assert "Updated GitHub Actions permissions successfully" in message

#         # Verify the API calls
#         assert self.repository._requester.requestJsonAndCheck.call_count == 2
#         self.repository._requester.requestJsonAndCheck.assert_any_call(
#             "PUT",
#             "/repos/test-owner/test-repo/actions/permissions",
#             input={"enabled": True, "allowed_actions": "selected"}
#         )
#         self.repository._requester.requestJsonAndCheck.assert_any_call(
#             "PUT",
#             "/repos/test-owner/test-repo/actions/permissions/selected-actions",
#             input={
#                 "github_owned_allowed": True,
#                 "verified_allowed": True,
#                 "patterns_allowed": ["owner/repo"]
#             }
#         )

#     def test_fix_dry_run(self):
#         """Test fixing GitHub Actions permissions in dry run mode."""
#         # Set dry_run to True
#         self.context.dry_run = True

#         # Create rule
#         rule = GitHubActionsEnabledRule()

#         # Apply the fix
#         success, message = rule.fix(self.context)

#         # Verify the result
#         assert success
#         assert "Would update GitHub Actions permissions (dry run)" in message

#         # Verify no API calls were made
#         self.repository._requester.requestJsonAndCheck.assert_not_called()

#     def test_fix_api_error(self):
#         """Test fixing GitHub Actions permissions when API call fails."""
#         # Configure the mock repository to raise an exception
#         self.repository._requester.requestJsonAndCheck.side_effect = GithubException(
#             500, {"message": "API error"}
#         )

#         # Create rule
#         rule = GitHubActionsEnabledRule()

#         # Apply the fix
#         success, message = rule.fix(self.context)

#         # Verify the result
#         assert not success
#         assert "Failed to update GitHub Actions permissions" in message
