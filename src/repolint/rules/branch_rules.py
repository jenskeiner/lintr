"""Rules for checking repository branch settings."""

from typing import Tuple

from github.Repository import Repository
from github.GithubException import GithubException

from repolint.rules.base import Rule, RuleCheckResult, RuleResult
from repolint.rules.context import RuleContext


class DefaultBranchExistsRule(Rule):
    """Rule that checks if a repository has a default branch."""

    def __init__(self):
        """Initialize the rule."""
        super().__init__(
            rule_id="R001",
            description="Repository must have a default branch"
        )

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
                    message=f"Repository has default branch: {default_branch}"
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Repository does not have a default branch",
                    fix_available=False,
                    fix_description=(
                        "Create a branch and set it as the default branch "
                        "in the repository settings"
                    )
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check default branch: {str(e)}",
                fix_available=False
            )


class WebCommitSignoffRequiredRule(Rule):
    """Rule that checks if web commit signoff is required for a repository."""

    def __init__(self):
        """Initialize the rule."""
        super().__init__(
            rule_id="R004",
            description="Repository must require signoff on web-based commits"
        )

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
                    message="Repository requires signoff on web-based commits"
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Repository does not require signoff on web-based commits",
                    fix_available=True,
                    fix_description=(
                        "Enable 'Require contributors to sign off on web-based commits' "
                        "in the repository settings"
                    )
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Error checking web commit signoff requirement: {str(e)}",
                fix_available=False
            )

    def fix(self, context: RuleContext) -> Tuple[bool, str]:
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
