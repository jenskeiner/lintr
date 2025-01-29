"""Rules for checking GitFlow branch naming conventions."""

from github.GithubException import GithubException

from repolint.rules.base import Rule, RuleCheckResult, RuleResult
from repolint.rules.context import RuleContext


class GitFlowBranchNamingRule(Rule):
    """Rule that checks if branch names conform to GitFlow conventions."""

    def __init__(self):
        """Initialize the rule."""
        super().__init__(
            rule_id="GF001",
            description="Branch names must conform to GitFlow conventions",
        )

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if branch names conform to GitFlow conventions.

        GitFlow branches must follow these conventions:
        - Must have either 'master' or 'main' branch
        - Must have 'develop' branch
        - Feature branches must start with 'feature/'
        - Release branches must start with 'release/'
        - Hotfix branches must start with 'hotfix/'
        - Support branches must start with 'support/'
        - Dependabot branches must start with 'dependabot/'

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            # Get all branches
            branches = list(context.repository.get_branches())
            branch_names = [b.name for b in branches]

            # Check for main/master branch
            has_main = "main" in branch_names or "master" in branch_names
            if not has_main:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Repository must have either 'main' or 'master' branch",
                    fix_available=False,
                )

            # Check for develop branch
            if "develop" not in branch_names:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Repository must have a 'develop' branch",
                    fix_available=False,
                )

            # Check other branch naming conventions
            invalid_branches = []
            for branch in branch_names:
                # Skip main/master and develop branches as they were checked above
                if branch in ["main", "master", "develop"]:
                    continue

                # Check if branch follows GitFlow naming conventions or is a Dependabot branch
                valid_prefixes = [
                    "feature/",
                    "release/",
                    "hotfix/",
                    "support/",
                    "dependabot/",
                ]
                if not any(branch.startswith(prefix) for prefix in valid_prefixes):
                    invalid_branches.append(branch)

            if invalid_branches:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message=(
                        f"The following branches do not follow GitFlow naming conventions: "
                        f"{', '.join(invalid_branches)}. Branch names should start with "
                        f"one of: feature/, release/, hotfix/, support/, or dependabot/"
                    ),
                    fix_available=False,
                )

            return RuleCheckResult(
                result=RuleResult.PASSED,
                message="All branch names conform to GitFlow conventions",
            )

        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check branch names: {str(e)}",
                fix_available=False,
            )


class GitFlowDefaultBranchRule(Rule):
    """Rule that checks if 'develop' is the default branch."""

    def __init__(self):
        """Initialize the rule."""
        super().__init__(
            rule_id="GF002",
            description="Default branch must be 'develop'",
        )

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if 'develop' is the default branch.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            default_branch = context.repository.default_branch

            if default_branch != "develop":
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message=f"Default branch is '{default_branch}' but should be 'develop'",
                    fix_available=True,
                )

            return RuleCheckResult(
                result=RuleResult.PASSED,
                message="Default branch is correctly set to 'develop'",
            )

        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check default branch: {str(e)}",
                fix_available=False,
            )

    def fix(self, context: RuleContext) -> bool:
        """Fix the default branch by setting it to 'develop'.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            True if the fix was successful, False otherwise.
        """
        try:
            # First check if develop branch exists
            branches = list(context.repository.get_branches())
            if not any(b.name == "develop" for b in branches):
                return False

            # Update default branch to develop
            context.repository.edit(default_branch="develop")
            return True

        except GithubException:
            return False
