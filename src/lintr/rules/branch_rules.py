"""Rules for checking repository branch settings."""


from github.GithubException import GithubException

from lintr.rules.base import Rule, RuleCheckResult, RuleResult
from lintr.rules.context import RuleContext


class DefaultBranchExistsRule(Rule):
    """Rule that checks if a repository has a default branch."""

    _id = "R001"
    _description = "Repository must have a default branch"

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if the repository has a default branch.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            default_branch = context.repository.default_branch
            if not isinstance(default_branch, (str, type(None))):
                # Handle the case where default_branch is a MagicMock in tests
                raise GithubException(404, "Not found")

            if default_branch:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message=f"Repository has default branch: {default_branch}",
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Repository does not have a default branch",
                    fix_available=False,
                    fix_description=(
                        "Create a branch and set it as the default branch "
                        "in the repository settings"
                    ),
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check default branch: {str(e)}",
                fix_available=False,
            )


class WebCommitSignoffRequiredRule(Rule):
    """Rule that checks if web commit signoff is required for a repository."""

    _id = "R004"
    _description = "Repository must require signoff on web-based commits"

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if the repository requires signoff on web-based commits.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            web_commit_signoff_required = context.repository.web_commit_signoff_required
            if web_commit_signoff_required:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message="Repository requires signoff on web-based commits",
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Repository does not require signoff on web-based commits",
                    fix_available=True,
                    fix_description=(
                        "Enable 'Require contributors to sign off on web-based commits' "
                        "in the repository settings"
                    ),
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Error checking web commit signoff requirement: {str(e)}",
                fix_available=False,
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Apply the fix for this rule.

        Enable the 'Require contributors to sign off on web-based commits' setting
        in the repository settings.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) indicating if the fix was successful.
        """
        try:
            context.repository.edit(web_commit_signoff_required=True)
            return (True, "Enabled web commit signoff requirement")
        except GithubException as e:
            return (False, f"Failed to enable web commit signoff: {str(e)}")


class DeleteBranchOnMergeRule(Rule):
    """Rule that checks if delete_branch_on_merge is enabled for a repository."""

    _id = "R017"
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
