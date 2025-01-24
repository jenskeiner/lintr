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
