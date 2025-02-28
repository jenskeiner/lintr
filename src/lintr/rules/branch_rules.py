"""Rules for checking repository branch settings."""

from abc import ABC
from github.GithubException import GithubException

from lintr.rules.base import (
    Rule,
    RuleCheckResult,
    RuleResult,
    BaseRuleConfig,
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
