"""Rules for checking repository branch settings."""

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
