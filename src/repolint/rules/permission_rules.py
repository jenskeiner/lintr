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
            description="Repository must have only one owner or admin (the user)"
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
                    message=f"Repository has only one admin: {authenticated_user}"
                )
            else:
                other_admins = [login for login in admin_logins if login != authenticated_user]
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message=(
                        f"Repository has {admin_count} admins. "
                        f"Other admins besides {authenticated_user}: {', '.join(other_admins)}"
                    ),
                    fix_available=False,
                    fix_description=(
                        "Remove admin access from other users in the repository settings"
                    )
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check repository admins: {str(e)}",
                fix_available=False
            )
