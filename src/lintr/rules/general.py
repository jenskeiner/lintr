"""Rules for checking repository archive settings."""
from abc import ABC, abstractmethod

from github import GithubException

from lintr.rules.base import (
    Rule,
    RuleCheckResult,
    RuleResult,
    RuleCategory,
    BaseRuleConfig,
)
from lintr.rules.context import RuleContext


class BinaryFlagRuleConfig(BaseRuleConfig):
    target: bool


class BinarySettingRule(Rule[BinaryFlagRuleConfig], ABC):
    """Abstract base class for rules that check a boolean setting on a repository."""

    _category = RuleCategory.GENERAL

    @abstractmethod
    def get_current_value(self, context: RuleContext) -> bool:
        """Get the current value of the setting from the repository.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            The current value of the setting.
        """
        pass

    @abstractmethod
    def update_setting(self, context: RuleContext, value: bool) -> None:
        """Update the setting to the given value.

        Args:
            context: Context object containing all information needed for the fix.
            value: The value to set.
        """
        pass

    @abstractmethod
    def get_setting_name(self) -> str:
        """Get the human-readable name of the setting.

        Returns:
            The name of the setting.
        """
        pass

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if the repository setting matches the target value.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        setting_name = self.get_setting_name()

        try:
            current_value = self.get_current_value(context)

            if current_value == self.config.target:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message=f"{setting_name.capitalize()} is {'enabled' if self.config.target else 'disabled'}.",
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message=f"{setting_name.capitalize()} is {'disabled' if self.config.target else 'enabled'}.",
                    fix_available=True,
                    fix_description=f"{'Enable' if self.config.target else 'Disable'} {setting_name} in repository settings.",
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.SKIPPED,
                message=f"Failed to check {setting_name} status: {str(e)}",
                fix_available=False,
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Apply the fix for this rule.

        Update the repository setting to match the target value.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) indicating if the fix was successful.
        """
        setting_name = self.get_setting_name()

        try:
            if context.dry_run:
                return (
                    True,
                    f"Would {'enable' if self.config.target else 'disable'} {setting_name}.",
                )
            self.update_setting(context, self.config.target)
            setting_name = self.get_setting_name()
            return (
                True,
                f"{setting_name.capitalize()} has been {'enabled' if self.config.target else 'disabled'}.",
            )
        except GithubException as e:
            setting_name = self.get_setting_name()
            return (
                False,
                f"Failed to {'enable' if self.config.target else 'disable'} {setting_name}: {str(e)}",
            )


class WebCommitSignoffRequiredRule(BinarySettingRule, ABC):
    """Rule that checks if web commit signoff is required for a repository."""

    def get_current_value(self, context: RuleContext) -> bool:
        """Get the current value of web commit signoff required setting.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Whether web commit signoff is required.
        """
        return context.repository.web_commit_signoff_required

    def update_setting(self, context: RuleContext, value: bool) -> None:
        """Update the web commit signoff required setting.

        Args:
            context: Context object containing all information needed for the fix.
            value: The value to set.
        """
        context.repository.edit(web_commit_signoff_required=value)

    def get_setting_name(self) -> str:
        """Get the human-readable name of the setting.

        Returns:
            The name of the setting.
        """
        return "'Require contributors to sign off on web-based commits'"


class WebCommitSignoffRequiredEnabledRule(WebCommitSignoffRequiredRule):
    """Rule that checks if web commit signoff is required for a repository."""

    _id = "G001P"
    _config = BinaryFlagRuleConfig(target=True)
    _description = "Checks that the repository has _Require contributors to sign off on web-based commits_ enabled in the General settings."
    _mutually_exclusive_with = ["G001N"]


class WebCommitSignoffRequiredDisabledRule(WebCommitSignoffRequiredRule):
    """Rule that checks if web commit signoff is required for a repository."""

    _id = "G001N"
    _config = BinaryFlagRuleConfig(target=False)
    _description = "Checks that the repository has _Require contributors to sign off on web-based commits_ disabled in the General settings."


class WikisRule(BinarySettingRule, ABC):
    """Rule that checks if wikis are disabled for a repository."""

    def get_current_value(self, context: RuleContext) -> bool:
        """Get the current value of the wikis setting.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Whether wikis are enabled.
        """
        return context.repository.has_wiki

    def update_setting(self, context: RuleContext, value: bool) -> None:
        """Update the wikis setting.

        Args:
            context: Context object containing all information needed for the fix.
            value: The value to set.
        """
        context.repository.edit(has_wiki=value)

    def get_setting_name(self) -> str:
        """Get the human-readable name of the setting.

        Returns:
            The name of the setting.
        """
        return "Wikis"


class WikisEnabledRule(WikisRule):
    _id = "G002P"
    _config = BinaryFlagRuleConfig(target=True)
    _description = "Checks that _Wikis_ are enabled in the General settings."


class WikisDisabledRule(WikisRule):
    _id = "G002N"
    _config = BinaryFlagRuleConfig(target=False)
    _description = "Checks that _Wikis_ are disabled in the General settings."


class IssuesRule(BinarySettingRule, ABC):
    """Rule that checks if issues are enabled/disabled for a repository."""

    def get_current_value(self, context: RuleContext) -> bool:
        """Get the current value of the issues setting.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Whether issues are enabled.
        """
        return context.repository.has_issues

    def update_setting(self, context: RuleContext, value: bool) -> None:
        """Update the issues setting.

        Args:
            context: Context object containing all information needed for the fix.
            value: The value to set.
        """
        context.repository.edit(has_issues=value)

    def get_setting_name(self) -> str:
        """Get the human-readable name of the setting.

        Returns:
            The name of the setting.
        """
        return "Issues"


class IssuesEnabledRule(IssuesRule):
    _id = "G003P"
    _config = BinaryFlagRuleConfig(target=True)
    _description = "Checks that _Issues_ are enabled in the General settings."


class IssuesDisabledRule(IssuesRule):
    _id = "G003N"
    _config = BinaryFlagRuleConfig(target=False)
    _description = "Checks that _Issues_ are disabled in the General settings."


class PreserveRepositoryRule(BinarySettingRule, ABC):
    """Rule that checks if 'Preserve this repository' is enabled."""

    def get_current_value(self, context: RuleContext) -> bool:
        """Get the current value of the preserve repository setting.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Whether the repository is archived.
        """
        return context.repository.archived

    def update_setting(self, context: RuleContext, value: bool) -> None:
        """Update the preserve repository setting.

        Args:
            context: Context object containing all information needed for the fix.
            value: The value to set.
        """
        context.repository.edit(archived=value)

    def get_setting_name(self) -> str:
        """Get the human-readable name of the setting.

        Returns:
            The name of the setting.
        """
        return "'Preserve this repository'"


class PreserveRepositoryEnabledRule(PreserveRepositoryRule):
    """Rule that checks if 'Preserve this repository' is enabled."""

    _id = "G004P"
    _config = BinaryFlagRuleConfig(target=True)
    _description = "Checks that the repository has 'Preserve this repository' enabled in the General settings."


class PreserveRepositoryDisabledRule(PreserveRepositoryRule):
    """Rule that checks if 'Preserve this repository' is disabled."""

    _id = "G004N"
    _config = BinaryFlagRuleConfig(target=False)
    _description = "Checks that the repository has 'Preserve this repository' disabled in the General settings."


class DiscussionsRule(BinarySettingRule, ABC):
    """Rule that checks if Discussions are disabled."""

    def get_current_value(self, context: RuleContext) -> bool:
        """Get the current value of the discussions setting.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Whether discussions are enabled.
        """
        return context.repository.has_discussions

    def update_setting(self, context: RuleContext, value: bool) -> None:
        """Update the discussions setting.

        Args:
            context: Context object containing all information needed for the fix.
            value: The value to set.
        """
        context.repository.edit(has_discussions=value)

    def get_setting_name(self) -> str:
        """Get the human-readable name of the setting.

        Returns:
            The name of the setting.
        """
        return "Discussions"


class DiscussionsDisabledRule(DiscussionsRule):
    _id = "G005N"
    _description = "Checks that Discussions are disabled in the General settings."
    _config = BinaryFlagRuleConfig(target=False)


class DiscussionsEnabledRule(DiscussionsRule):
    _id = "G005P"
    _description = "Checks that Discussions are enabled in the General settings."
    _config = BinaryFlagRuleConfig(target=True)


class ProjectsRule(BinarySettingRule, ABC):
    """Rule that checks if Projects are disabled."""

    def get_current_value(self, context: RuleContext) -> bool:
        """Get the current value of the projects setting.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Whether projects are enabled.
        """
        return context.repository.has_projects

    def update_setting(self, context: RuleContext, value: bool) -> None:
        """Update the projects setting.

        Args:
            context: Context object containing all information needed for the fix.
            value: The value to set.
        """
        context.repository.edit(has_projects=value)

    def get_setting_name(self) -> str:
        """Get the human-readable name of the setting.

        Returns:
            The name of the setting.
        """
        return "Projects"


class ProjectsDisabledRule(ProjectsRule):
    """Rule that checks if Projects are disabled."""

    _id = "G006N"
    _description = "Checks that Projects are disabled in the General settings."
    _config = BinaryFlagRuleConfig(target=False)


class ProjectsEnabledRule(ProjectsRule):
    """Rule that checks if Projects are enabled."""

    _id = "G006P"
    _description = "Checks that Projects are enabled in the General settings."
    _config = BinaryFlagRuleConfig(target=True)


class MergeCommitsRule(BinarySettingRule, ABC):
    """Rule that checks if merge commits are allowed for pull requests."""

    def get_current_value(self, context: RuleContext) -> bool:
        """Get the current value of the merge commits setting.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Whether merge commits are allowed.
        """
        return context.repository.allow_merge_commit

    def update_setting(self, context: RuleContext, value: bool) -> None:
        """Update the merge commits setting.

        Args:
            context: Context object containing all information needed for the fix.
            value: The value to set.
        """
        context.repository.edit(allow_merge_commit=value)

    def get_setting_name(self) -> str:
        """Get the human-readable name of the setting.

        Returns:
            The name of the setting.
        """
        return "merge commits"


class MergeCommitsDisabledRule(MergeCommitsRule):
    """Rule that checks if merge commits are allowed for pull requests."""

    _id = "G007N"
    _description = "Checks that merge commits are disabled for pull requests."
    _config = BinaryFlagRuleConfig(target=False)


class MergeCommitsEnabledRule(MergeCommitsRule):
    """Rule that checks if merge commits are allowed for pull requests."""

    _id = "G007P"
    _description = "Checks that merge commits are enabled for pull requests."
    _config = BinaryFlagRuleConfig(target=True)


class SquashMergeRule(BinarySettingRule, ABC):
    """Rule that checks if squash merging is enabled/disabled for pull requests."""

    _category = RuleCategory.GENERAL

    def get_current_value(self, context: RuleContext) -> bool:
        """Get the current value of the squash merge setting.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Whether squash merging is enabled.
        """
        return context.repository.allow_squash_merge

    def update_setting(self, context: RuleContext, value: bool) -> None:
        """Update the squash merge setting.

        Args:
            context: Context object containing all information needed for the fix.
            value: The value to set.
        """
        context.repository.edit(allow_squash_merge=value)

    def get_setting_name(self) -> str:
        """Get the human-readable name of the setting.

        Returns:
            The name of the setting.
        """
        return "squash merging"


class SquashMergeDisabledRule(SquashMergeRule):
    """Rule that checks if squash merging is disabled for pull requests."""

    _id = "G008N"
    _description = "Checks that squash merging is disabled for pull requests."
    _config = BinaryFlagRuleConfig(target=False)


class SquashMergeEnabledRule(SquashMergeRule):
    """Rule that checks if squash merging is enabled for pull requests."""

    _id = "G008P"
    _description = "Checks that squash merging is enabled for pull requests."
    _config = BinaryFlagRuleConfig(target=True)


class RebaseMergeRule(BinarySettingRule, ABC):
    """Rule that checks if rebase merging is enabled/disabled for pull requests."""

    _category = RuleCategory.GENERAL

    def get_current_value(self, context: RuleContext) -> bool:
        """Get the current value of the rebase merge setting.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Whether rebase merging is enabled.
        """
        return context.repository.allow_rebase_merge

    def update_setting(self, context: RuleContext, value: bool) -> None:
        """Update the rebase merge setting.

        Args:
            context: Context object containing all information needed for the fix.
            value: The value to set.
        """
        context.repository.edit(allow_rebase_merge=value)

    def get_setting_name(self) -> str:
        """Get the human-readable name of the setting.

        Returns:
            The name of the setting.
        """
        return "rebase merging"


class RebaseMergeDisabledRule(RebaseMergeRule):
    """Rule that checks if rebase merging is disabled for pull requests."""

    _id = "G009N"
    _description = "Checks that rebase merging is disabled for pull requests."
    _config = BinaryFlagRuleConfig(target=False)


class RebaseMergeEnabledRule(RebaseMergeRule):
    """Rule that checks if rebase merging is enabled for pull requests."""

    _id = "G009P"
    _description = "Checks that rebase merging is enabled for pull requests."
    _config = BinaryFlagRuleConfig(target=True)


class AutoMergeRule(BinarySettingRule, ABC):
    """Rule that checks if auto merge is enabled/disabled for a repository."""

    _category = RuleCategory.GENERAL

    def get_current_value(self, context: RuleContext) -> bool:
        """Get the current value of the auto merge setting.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Whether auto merge is enabled.
        """
        return context.repository.allow_auto_merge

    def update_setting(self, context: RuleContext, value: bool) -> None:
        """Update the auto merge setting.

        Args:
            context: Context object containing all information needed for the fix.
            value: The value to set.
        """
        context.repository.edit(allow_auto_merge=value)

    def get_setting_name(self) -> str:
        """Get the human-readable name of the setting.

        Returns:
            The name of the setting.
        """
        return "auto merge"


class AutoMergeDisabledRule(AutoMergeRule):
    """Rule that checks if auto merge is disabled for a repository."""

    _id = "G010N"
    _description = "Checks that 'Allow auto-merge' is disabled for a repository."
    _config = BinaryFlagRuleConfig(target=False)


class AutoMergeEnabledRule(AutoMergeRule):
    """Rule that checks if auto merge is enabled for a repository."""

    _id = "G010P"
    _description = "Checks that 'Allow auto-merge' is enabled for a repository."
    _config = BinaryFlagRuleConfig(target=True)


class DeleteBranchOnMergeRule(BinarySettingRule, ABC):
    """Rule that checks if delete_branch_on_merge is enabled/disabled for a repository."""

    _category = RuleCategory.GENERAL

    def get_current_value(self, context: RuleContext) -> bool:
        """Get the current value of the delete_branch_on_merge setting.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Whether delete_branch_on_merge is enabled.
        """
        return context.repository.delete_branch_on_merge

    def update_setting(self, context: RuleContext, value: bool) -> None:
        """Update the delete_branch_on_merge setting.

        Args:
            context: Context object containing all information needed for the fix.
            value: The value to set.
        """
        context.repository.edit(delete_branch_on_merge=value)

    def get_setting_name(self) -> str:
        """Get the human-readable name of the setting.

        Returns:
            The name of the setting.
        """
        return "'Automatically delete head branches'"


class DeleteBranchOnMergeDisabledRule(DeleteBranchOnMergeRule):
    """Rule that checks if delete_branch_on_merge is disabled for a repository."""

    _id = "G011N"
    _description = (
        "Checks that automatically delete head branches is disabled for a repository."
    )
    _config = BinaryFlagRuleConfig(target=False)


class DeleteBranchOnMergeEnabledRule(DeleteBranchOnMergeRule):
    """Rule that checks if delete_branch_on_merge is enabled for a repository."""

    _id = "G011P"
    _description = (
        "Checks that automatically delete head branches is enabled for a repository."
    )
    _config = BinaryFlagRuleConfig(target=True)
