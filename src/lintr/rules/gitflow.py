"""Rules for checking GitFlow branch naming conventions."""

from github.GithubException import GithubException

from lintr.rules.base import Rule, RuleCheckResult, RuleResult
from lintr.rules.context import RuleContext
from lintr.rules.branch_rules import DefaultBranchNameRule, DefaultBranchNameRuleConfig


class GitFlowBranchNamingRule(Rule):
    """Rule that checks if branch names conform to GitFlow conventions."""

    _id = "GF001"
    _description = "Branch names must conform to GitFlow conventions"

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


class GitFlowDefaultBranchRule(DefaultBranchNameRule):
    """Rule that checks if 'develop' is the default branch."""

    _id = "GF002"
    _description = "Default branch must be 'develop'"
    _config = DefaultBranchNameRuleConfig(branch="develop")
    _example = _config
