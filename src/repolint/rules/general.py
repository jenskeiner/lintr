"""Rules for checking repository archive settings."""

from github.GithubException import GithubException

from repolint.rules.base import Rule, RuleCheckResult, RuleResult
from repolint.rules.context import RuleContext


class PreserveRepositoryRule(Rule):
    """Rule that checks if 'Preserve this repository' is enabled."""

    def __init__(self):
        """Initialize the rule."""
        super().__init__(
            rule_id="R011",
            description="Repository must have 'Preserve this repository' enabled",
        )

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if 'Preserve this repository' is enabled for the repository.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            # Check if the repository is archived
            is_archived = context.repository.archived

            if is_archived:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message="Repository is preserved (archived)",
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Repository is not preserved (not archived)",
                    fix_available=True,
                    fix_description="Enable 'Preserve this repository' in repository settings",
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.SKIPPED,
                message=f"Failed to check repository archive status: {str(e)}",
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Apply the fix for this rule.

        Enable 'Preserve this repository' in repository settings.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) indicating if the fix was successful.
        """
        try:
            if context.dry_run:
                return True, "Would enable 'Preserve this repository'"

            # Archive the repository
            context.repository.edit(archived=True)
            return True, "Successfully enabled 'Preserve this repository'"
        except GithubException as e:
            return False, f"Failed to enable 'Preserve this repository': {str(e)}"
