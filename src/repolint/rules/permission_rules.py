"""Rules for checking repository permission settings."""


from github.GithubException import GithubException

from repolint.rules.base import Rule, RuleCheckResult, RuleResult
from repolint.rules.context import RuleContext


class SingleOwnerRule(Rule):
    """Rule that checks if the user is the only owner or admin of the repository."""

    def __init__(self):
        """Initialize the rule."""
        super().__init__(
            rule_id="R005",
            description="Repository must have only one owner or admin (the user)",
        )

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if the repository has only one owner or admin (the user).

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            # Get all collaborators with their permissions
            collaborators = context.repository.get_collaborators()

            # Get the authenticated user's login
            authenticated_user = context.repository.owner.login

            # Count owners/admins
            admin_count = 0
            admin_logins = []

            for collaborator in collaborators:
                # Get the permission level for this collaborator
                permission = collaborator.permissions

                # Check if they have admin access
                if permission.admin:
                    admin_count += 1
                    admin_logins.append(collaborator.login)

            # If there's only one admin and it's the authenticated user, we pass
            if admin_count == 1 and authenticated_user in admin_logins:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message=f"Repository has only one admin: {authenticated_user}",
                )
            else:
                other_admins = [
                    login for login in admin_logins if login != authenticated_user
                ]
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message=(
                        f"Repository has {admin_count} admins. "
                        f"Other admins besides {authenticated_user}: {', '.join(other_admins)}"
                    ),
                    fix_available=False,
                    fix_description=(
                        "Remove admin access from other users in the repository settings"
                    ),
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check repository admins: {str(e)}",
                fix_available=False,
            )


class NoCollaboratorsRule(Rule):
    """Rule that checks if a repository has no collaborators other than the user."""

    def __init__(self):
        """Initialize the rule."""
        super().__init__(
            rule_id="R006",
            description="Repository must have no collaborators other than the user",
        )

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if the repository has no collaborators other than the user.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            # Get all collaborators
            collaborators = context.repository.get_collaborators()

            # Get the authenticated user's login
            authenticated_user = context.repository.owner.login

            # Check for any collaborators other than the user
            other_collaborators = []
            for collaborator in collaborators:
                if collaborator.login != authenticated_user:
                    other_collaborators.append(collaborator.login)

            if not other_collaborators:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message="Repository has no collaborators other than the user",
                    fix_available=False,
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message=f"Repository has {len(other_collaborators)} other collaborators: {', '.join(other_collaborators)}",
                    fix_available=True,
                    fix_description=f"Remove collaborators: {', '.join(other_collaborators)}",
                )

        except Exception as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check collaborators: {str(e)}",
                fix_available=False,
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Remove all collaborators from the repository except the user.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) indicating if the fix was successful.
        """
        try:
            # Get all collaborators
            collaborators = context.repository.get_collaborators()

            # Get the authenticated user's login
            authenticated_user = context.repository.owner.login

            # Remove all collaborators except the user
            removed_collaborators = []
            for collaborator in collaborators:
                if collaborator.login != authenticated_user:
                    context.repository.remove_from_collaborators(collaborator.login)
                    removed_collaborators.append(collaborator.login)

            if removed_collaborators:
                return (
                    True,
                    f"Removed collaborators: {', '.join(removed_collaborators)}",
                )
            else:
                return True, "No collaborators needed to be removed"

        except Exception as e:
            return False, f"Failed to remove collaborators: {str(e)}"


class WikisDisabledRule(Rule):
    """Rule that checks if wikis are disabled for a repository."""

    def __init__(self):
        """Initialize the rule."""
        super().__init__(
            rule_id="R007",
            description="Repository must have wikis disabled",
        )

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if wikis are disabled for the repository.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            if not context.repository.has_wiki:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message="Wikis are disabled",
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Wikis are enabled",
                    fix_available=True,
                    fix_description="Disable wikis in repository settings",
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check wiki status: {str(e)}",
                fix_available=False,
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Apply the fix for this rule.

        Disable wikis in the repository settings.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) indicating if the fix was successful.
        """
        try:
            context.repository.edit(has_wiki=False)
            return True, "Wikis have been disabled"
        except GithubException as e:
            return False, f"Failed to disable wikis: {str(e)}"


class IssuesDisabledRule(Rule):
    """Rule that checks if issues are disabled for a repository."""

    def __init__(self):
        """Initialize the rule."""
        super().__init__(
            rule_id="R008",
            description="Repository must have issues disabled",
        )

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if issues are disabled for the repository.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            if not context.repository.has_issues:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message="Issues are disabled",
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Issues are enabled",
                    fix_available=True,
                    fix_description="Disable issues in repository settings",
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check issues status: {str(e)}",
                fix_available=False,
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Apply the fix for this rule.

        Disable issues in the repository settings.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) indicating if the fix was successful.
        """
        try:
            context.repository.edit(has_issues=False)
            return True, "Issues have been disabled"
        except GithubException as e:
            return False, f"Failed to disable issues: {str(e)}"


class MergeCommitsAllowedRule(Rule):
    """Rule that checks if merge commits are allowed for pull requests."""

    def __init__(self):
        """Initialize the rule."""
        super().__init__(
            rule_id="R014",
            description="Repository must allow merge commits for pull requests",
        )

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if merge commits are allowed for pull requests.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            # Check if merge commits are allowed
            if context.repository.allow_merge_commit:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message="Merge commits are allowed for pull requests",
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Merge commits are not allowed for pull requests",
                    fix_available=True,
                    fix_description="Enable merge commits in repository settings",
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check merge commit status: {str(e)}",
                fix_available=False,
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Apply the fix for this rule.

        Enable merge commits in repository settings.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) indicating if the fix was successful.
        """
        try:
            # Enable merge commits
            context.repository.edit(allow_merge_commit=True)
            return True, "Enabled merge commits for pull requests"
        except GithubException as e:
            return False, f"Failed to enable merge commits: {str(e)}"


class SquashMergeDisabledRule(Rule):
    """Rule that checks if squash merging is disabled for pull requests."""

    def __init__(self):
        """Initialize the rule."""
        super().__init__(
            rule_id="R015",
            description="Repository must have squash merging disabled for pull requests",
        )

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if squash merging is disabled for pull requests.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            # Check if squash merging is disabled
            if not context.repository.allow_squash_merge:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message="Squash merging is disabled for pull requests",
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Squash merging is enabled for pull requests",
                    fix_available=True,
                    fix_description="Disable squash merging in repository settings",
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check squash merge status: {str(e)}",
                fix_available=False,
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Apply the fix for this rule.

        Disable squash merging in repository settings.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) indicating if the fix was successful.
        """
        try:
            # Disable squash merging
            context.repository.edit(allow_squash_merge=False)
            return True, "Disabled squash merging for pull requests"
        except GithubException as e:
            return False, f"Failed to disable squash merging: {str(e)}"


class RebaseMergeDisabledRule(Rule):
    """Rule that checks if rebase merging is disabled for pull requests."""

    def __init__(self):
        """Initialize the rule."""
        super().__init__(
            rule_id="R016",
            description="Repository must have rebase merging disabled for pull requests",
        )

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if rebase merging is disabled for pull requests.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            # Check if rebase merging is disabled
            if not context.repository.allow_rebase_merge:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message="Rebase merging is disabled for pull requests",
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Rebase merging is enabled for pull requests",
                    fix_available=True,
                    fix_description="Disable rebase merging in repository settings",
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check rebase merge status: {str(e)}",
                fix_available=False,
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Apply the fix for this rule.

        Disable rebase merging in repository settings.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) indicating if the fix was successful.
        """
        try:
            # Disable rebase merging
            context.repository.edit(allow_rebase_merge=False)
            return True, "Disabled rebase merging for pull requests"
        except GithubException as e:
            return False, f"Failed to disable rebase merging: {str(e)}"
