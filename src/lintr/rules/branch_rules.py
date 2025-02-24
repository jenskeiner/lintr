"""Rules for checking repository branch settings."""

from abc import ABC
from github.GithubException import GithubException

from lintr.rules.base import (
    Rule,
    RuleCheckResult,
    RuleResult,
    BaseRuleConfig,
    RuleCategory,
)
from lintr.rules.context import RuleContext


class DefaultBranchNameRuleConfig(BaseRuleConfig):
    branch: str


class DefaultBranchNameRule(Rule[DefaultBranchNameRuleConfig], ABC):
    """Rule that checks if the default branch matches the configured branch."""

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if the default branch matches the configured branch.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            default_branch = context.repository.default_branch

            if default_branch != self.config.branch:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message=f"Default branch is '{default_branch}' but should be '{self.config.branch}'",
                    fix_available=True,
                )

            return RuleCheckResult(
                result=RuleResult.PASSED,
                message=f"Default branch is correctly set to '{self.config.branch}'",
            )

        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check default branch: {str(e)}",
                fix_available=False,
            )

    def fix(self, context: RuleContext) -> bool:
        """Fix the default branch by setting it to the configured branch.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            True if the fix was successful, False otherwise.
        """
        try:
            # First check if develop branch exists
            branches = list(context.repository.get_branches())
            if not any(b.name == self.config.branch for b in branches):
                return False

            # Update default branch to develop
            context.repository.edit(default_branch=self.config.branch)
            return True

        except GithubException:
            return False


class DeleteBranchOnMergeRule(Rule):
    """Rule that checks if delete_branch_on_merge is enabled for a repository."""

    _id = "R017"
    _category = RuleCategory.GENERAL
    _description = "Repository must have delete_branch_on_merge enabled"

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if the repository has delete_branch_on_merge enabled.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            delete_branch_on_merge = context.repository.delete_branch_on_merge
            if delete_branch_on_merge:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message="Repository has delete_branch_on_merge enabled",
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Repository does not have delete_branch_on_merge enabled",
                    fix_available=True,
                    fix_description=(
                        "Enable 'Automatically delete head branches' in the repository settings"
                    ),
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Error checking delete_branch_on_merge setting: {str(e)}",
                fix_available=False,
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Apply the fix for this rule.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) where success is a boolean indicating if
            the fix was successful, and message provides details about what was done
            or why the fix failed.
        """
        try:
            context.repository.edit(delete_branch_on_merge=True)
            return True, "Enabled delete_branch_on_merge setting"
        except GithubException as e:
            return False, f"Failed to enable delete_branch_on_merge setting: {str(e)}"


class AutoMergeDisabledRule(Rule):
    """Rule that checks if auto merge is disabled for a repository."""

    _id = "R018"
    _category = RuleCategory.GENERAL
    _description = "Repository must have auto merge disabled"

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if the repository has auto merge disabled.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            allow_auto_merge = context.repository.allow_auto_merge
            if not allow_auto_merge:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message="Repository has auto merge disabled",
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Repository has auto merge enabled",
                    fix_available=True,
                    fix_description=(
                        "Disable 'Allow auto-merge' in the repository settings"
                    ),
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Error checking auto merge setting: {str(e)}",
                fix_available=False,
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Apply the fix for this rule.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) where success is a boolean indicating if
            the fix was successful, and message provides details about what was done
            or why the fix failed.
        """
        try:
            context.repository.edit(allow_auto_merge=False)
            return True, "Disabled auto merge setting"
        except GithubException as e:
            return False, f"Failed to disable auto merge setting: {str(e)}"
