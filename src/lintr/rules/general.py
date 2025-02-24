"""Rules for checking repository archive settings."""
from abc import ABC

from github import GithubException

from lintr.rules.base import (
    Rule,
    RuleCheckResult,
    RuleResult,
    RuleCategory,
    BaseRuleConfig,
)
from lintr.rules.context import RuleContext


class WebCommitSignoffRequiredRuleConfig(BaseRuleConfig):
    target: bool


class WebCommitSignoffRequiredRule(Rule[WebCommitSignoffRequiredRuleConfig], ABC):
    """Rule that checks if web commit signoff is required for a repository."""

    _category = RuleCategory.GENERAL

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if the repository requires signoff on web-based commits.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            web_commit_signoff_required = context.repository.web_commit_signoff_required
            if web_commit_signoff_required == self.config.target:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message=f"'Require contributors to sign off on web-based commits' is set to {self.config.target}",
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message=f"'Require contributors to sign off on web-based commits' is set to {not self.config.target}",
                    fix_available=True,
                    fix_description=(
                        f"{'Enable' if self.config.target else 'Disable'} 'Require contributors to sign off on web-based commits' "
                        "in the repository settings."
                    ),
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Error checking 'Require contributors to sign off on web-based commits': {str(e)}",
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
            context.repository.edit(web_commit_signoff_required=self.config.target)
            return (
                True,
                f"{'Enabled' if self.config.target else 'Disabled'} 'Require contributors to sign off on web-based commits'.",
            )
        except GithubException as e:
            return (
                False,
                f"Failed to {'enable' if self.config.target else 'disable'} 'Require contributors to sign off on web-based commits': {str(e)}",
            )


class WebCommitSignoffRequiredEnabledRule(WebCommitSignoffRequiredRule):
    """Rule that checks if web commit signoff is required for a repository."""

    _id = "R001P"
    _config = WebCommitSignoffRequiredRuleConfig(target=True)
    _description = "Checks that the repository has `Require contributors to sign off on web-based commits` enabled in the General settings section."


class WebCommitSignoffRequiredDisabledRule(WebCommitSignoffRequiredRule):
    """Rule that checks if web commit signoff is required for a repository."""

    _id = "R001N"
    _config = WebCommitSignoffRequiredRuleConfig(target=False)
    _description = "Checks that the repository has `Require contributors to sign off on web-based commits` disabled in the General settings section."


class WikisDisabledRule(Rule):
    """Rule that checks if wikis are disabled for a repository."""

    _id = "R002"
    _description = "Checks that *Wikis* are disabled in the General settings section."

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

    _id = "R008"
    _description = "Repository must have issues disabled"

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


class PreserveRepositoryRule(Rule):
    """Rule that checks if 'Preserve this repository' is enabled."""

    _id = "R011"
    _category = RuleCategory.GENERAL
    _description = "Repository must have 'Preserve this repository' enabled"

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


class DiscussionsDisabledRule(Rule):
    """Rule that checks if Discussions are disabled."""

    _id = "R012"
    _category = RuleCategory.GENERAL
    _description = "Repository must have Discussions disabled"

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if Discussions are disabled for the repository.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            # Check if discussions are enabled
            has_discussions = context.repository.has_discussions

            if not has_discussions:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message="Repository has Discussions disabled",
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Repository has Discussions enabled",
                    fix_available=True,
                    fix_description="Disable Discussions in repository settings",
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.SKIPPED,
                message=f"Failed to check repository Discussions status: {str(e)}",
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Apply the fix for this rule.

        Disable Discussions in repository settings.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) indicating if the fix was successful.
        """
        try:
            if context.dry_run:
                return True, "Would disable Discussions"

            # Disable discussions
            context.repository.edit(has_discussions=False)
            return True, "Successfully disabled Discussions"
        except GithubException as e:
            return False, f"Failed to disable Discussions: {str(e)}"


class ProjectsDisabledRule(Rule):
    """Rule that checks if Projects are disabled."""

    _id = "R013"
    _category = RuleCategory.GENERAL
    _description = "Repository must have Projects disabled"

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if Projects are disabled for the repository.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            # Check if projects are enabled
            has_projects = context.repository.has_projects

            if not has_projects:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message="Repository has Projects disabled",
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Repository has Projects enabled",
                    fix_available=True,
                    fix_description="Disable Projects in repository settings",
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.SKIPPED,
                message=f"Failed to check repository Projects status: {str(e)}",
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Apply the fix for this rule.

        Disable Projects in repository settings.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) indicating if the fix was successful.
        """
        try:
            if context.dry_run:
                return True, "Would disable Projects"

            # Disable projects
            context.repository.edit(has_projects=False)
            return True, "Successfully disabled Projects"
        except GithubException as e:
            return False, f"Failed to disable Projects: {str(e)}"
