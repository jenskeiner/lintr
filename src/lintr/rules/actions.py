import abc
from difflib import unified_diff
from enum import Enum
from typing import Annotated, Generic, Literal, TypeVar, Union

from github.GithubException import GithubException
from pydantic import Field, TypeAdapter

from lintr.rules.base import (
    BaseRuleConfig,
    Rule,
    RuleCategory,
    RuleCheckResult,
    RuleResult,
)
from lintr.rules.context import RuleContext

# Constants for field descriptions
ACTIONS_ENABLED_DESCRIPTION = (
    "Whether GitHub Actions should be enabled for the repository"
)
ACTIONS_ALLOWED_DESCRIPTION = "Which actions are allowed to run"


# GitHub Actions permissions configuration
class AllowedActions(str, Enum):
    """Enum for allowed actions settings."""

    ALL = "all"
    LOCAL_ONLY = "local_only"
    SELECTED = "selected"


class ActionsPermissionsRuleConfig(BaseRuleConfig):
    pass


# Variant 1: Actions disabled
class ActionsDisabledRuleConfig(ActionsPermissionsRuleConfig):
    """Configuration when GitHub Actions are disabled."""

    enabled: Literal[False] = Field(
        default=False, description=ACTIONS_ENABLED_DESCRIPTION
    )


# Variant 2: Actions enabled with ALL policy
class ActionsEnabledAllRuleConfig(ActionsPermissionsRuleConfig):
    """Configuration when GitHub Actions are enabled with ALL policy."""

    enabled: Literal[True] = Field(
        default=True, description=ACTIONS_ENABLED_DESCRIPTION
    )
    allowed_actions: Literal[AllowedActions.ALL] = Field(
        default=AllowedActions.ALL, description=ACTIONS_ALLOWED_DESCRIPTION
    )


# Variant 3: Actions enabled with LOCAL_ONLY policy
class ActionsEnabledLocalOnlyRuleConfig(ActionsPermissionsRuleConfig):
    """Configuration when GitHub Actions are enabled with LOCAL_ONLY policy."""

    enabled: Literal[True] = Field(
        default=True, description=ACTIONS_ENABLED_DESCRIPTION
    )
    allowed_actions: Literal[AllowedActions.LOCAL_ONLY] = Field(
        default=AllowedActions.LOCAL_ONLY, description=ACTIONS_ALLOWED_DESCRIPTION
    )


# Variant 4: Actions enabled with SELECTED policy
class ActionsEnabledSelectedRuleConfig(ActionsPermissionsRuleConfig):
    """Configuration when GitHub Actions are enabled with SELECTED policy."""

    enabled: Literal[True] = Field(
        default=True, description=ACTIONS_ENABLED_DESCRIPTION
    )
    allowed_actions: Literal[AllowedActions.SELECTED] = Field(
        default=AllowedActions.SELECTED, description=ACTIONS_ALLOWED_DESCRIPTION
    )
    github_owned_allowed: bool = Field(
        default=False, description="Whether GitHub-owned actions are allowed"
    )
    verified_allowed: bool = Field(
        default=False, description="Whether verified actions are allowed"
    )
    patterns_allowed: list[str] = Field(
        default_factory=list,
        description="Specific patterns of actions that are allowed",
    )


# Tagged union for configurations that allow actions.
ActionsEnabledRuleConfig = Annotated[
    Union[
        ActionsEnabledAllRuleConfig,
        ActionsEnabledLocalOnlyRuleConfig,
        ActionsEnabledSelectedRuleConfig,
    ],
    Field(discriminator="allowed_actions"),
]

# Tagged union for the configuration
ActionsPermissionsRuleConfig = Annotated[
    Union[ActionsDisabledRuleConfig, ActionsEnabledRuleConfig],
    Field(discriminator="enabled"),
]

actions_permissions_rule_config_ta = TypeAdapter(ActionsPermissionsRuleConfig)

ActionsPermissionsRuleConfigT = TypeVar(
    "ActionsPermissionsRuleConfigT", bound=ActionsPermissionsRuleConfig
)


class GitHubActionsPermissionsRule(
    Generic[ActionsPermissionsRuleConfigT], Rule[ActionsPermissionsRuleConfig], abc.ABC
):
    """Rule that checks GitHub Actions permissions for a repository."""

    _id = "A001"
    _name = "github-actions-permissions"
    _category = RuleCategory.ACTIONS
    _description = "Checks GitHub Actions permissions for a repository"
    _example = ActionsEnabledSelectedRuleConfig(
        enabled=True,
        allowed_actions=AllowedActions.SELECTED,
        github_owned_allowed=True,
        verified_allowed=True,
        patterns_allowed=["owner/repo"],
    )

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check GitHub Actions permissions for a repository.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            # Get the repository object
            repo = context.repository

            # Use the underlying API to get GitHub Actions permissions
            # GET /repos/{owner}/{repo}/actions/permissions
            url = f"/repos/{repo.owner.login}/{repo.name}/actions/permissions"
            response = repo._requester.requestJsonAndCheck("GET", url)
            permissions = response[1]

            if (
                permissions.get("enabled")
                and permissions.get("allowed_actions") == "selected"
            ):
                selected_actions_url = permissions.pop("selected_actions_url")
                response = repo._requester.requestJsonAndCheck(
                    "GET", selected_actions_url
                )
                permissions.update(response[1])

            permissions = actions_permissions_rule_config_ta.validate_python(
                permissions
            )

            if permissions != self.config:
                diff_lines = unified_diff(
                    self.config.model_dump_json(indent=2).splitlines(),
                    permissions.model_dump_json(indent=2).splitlines(),
                    fromfile="expected",
                    tofile="actual",
                    n=500,
                )
                diff = []
                for line in diff_lines:
                    if line.startswith("+"):
                        colored_line = f"[yellow]          {line}[/yellow]"
                    elif line.startswith("-"):
                        colored_line = f"[red]          {line}[/red]"
                    else:
                        colored_line = f"          {line}"
                    diff.append(colored_line)

                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="\n".join(["Wrong GitHub Actions permissions:"] + diff),
                    fix_available=True,
                    fix_description="Update GitHub Actions permissions.",
                )

            # All checks passed
            return RuleCheckResult(
                result=RuleResult.PASSED,
                message="GitHub Actions permissions are correctly configured.",
            )

        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check GitHub Actions permissions: {str(e)}",
                fix_available=False,
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Apply the fix for this rule.

        Update GitHub Actions permissions for the repository.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) indicating if the fix was successful.
        """
        try:
            if context.dry_run:
                return True, "Would update GitHub Actions permissions (dry run)"

            # Get the repository object
            repo = context.repository

            # Update GitHub Actions permissions
            # PUT /repos/{owner}/{repo}/actions/permissions
            url = f"/repos/{repo.owner.login}/{repo.name}/actions/permissions"

            data = self.config.model_dump(include={"enabled", "allowed_actions"})

            repo._requester.requestJsonAndCheck("PUT", url, input=data)

            if data["allowed_actions"] == "selected":
                response = repo._requester.requestJsonAndCheck("GET", url)
                selected_actions_url = response[1].get("selected_actions_url")
                data = self.config.model_dump(
                    include={
                        "github_owned_allowed",
                        "verified_allowed",
                        "patterns_allowed",
                    }
                )
                repo._requester.requestJsonAndCheck(
                    "PUT", selected_actions_url, input=data
                )

            return True, "Updated GitHub Actions permissions successfully."

        except GithubException as e:
            return False, f"Failed to update GitHub Actions permissions: {str(e)}"


class GitHubActionsDisabledRule(
    GitHubActionsPermissionsRule[ActionsDisabledRuleConfig]
):
    """Rule that checks if GitHub Actions is disabled for a repository."""

    _id = "A001D"
    _name = "github-actions-disabled"
    _description = "Checks that GitHub Actions are disabled for the repository"
    _config = ActionsDisabledRuleConfig()
    _configurable = False


class GitHubActionsEnabledAllRule(
    GitHubActionsPermissionsRule[ActionsEnabledAllRuleConfig]
):
    """Rule that checks if GitHub Actions is disabled for a repository."""

    _id = "A001A"
    _name = "github-actions-enabled-all"
    _description = "Checks that all GitHub Actions are enabled for the repository"
    _config = ActionsEnabledAllRuleConfig()
    _configurable = False


class GitHubActionsEnabledLocalOnlyRule(
    GitHubActionsPermissionsRule[ActionsEnabledLocalOnlyRuleConfig]
):
    """Rule that checks if GitHub Actions is disabled for a repository."""

    _id = "A001L"
    _name = "github-actions-enabled-local-only"
    _description = (
        "Checks that only local GitHub Actions are enabled for the repository"
    )
    _config = ActionsEnabledLocalOnlyRuleConfig()
    _configurable = False


class GitHubActionsEnabledSelectedRule(
    GitHubActionsPermissionsRule[ActionsEnabledSelectedRuleConfig]
):
    """Rule that checks if GitHub Actions is disabled for a repository."""

    _id = "A001S"
    _name = "github-actions-enabled-selected"
    _description = (
        "Checks that only selected GitHub Actions are enabled for the repository"
    )
    _config = ActionsEnabledSelectedRuleConfig(
        enabled=True,
        allowed_actions="selected",
        github_owned_allowed=True,
        verified_allowed=True,
        patterns_allowed=[],
    )


class DefaultWorkflowPermissionsRuleConfig(BaseRuleConfig):
    default_workflow_permissions: Literal["read", "write"]
    can_approve_pull_request_reviews: bool


class GitHubActionsDefaultWorkflowPermissionsRule(
    Rule[DefaultWorkflowPermissionsRuleConfig]
):
    """Rule that checks GitHub Actions default workflow permissions for a repository."""

    _id = "A002"
    _name = "github-actions-default-workflow-permissions"
    _category = RuleCategory.ACTIONS
    _description = "Checks GitHub Actions default workflow permissions for a repository"
    _config = DefaultWorkflowPermissionsRuleConfig(
        default_workflow_permissions="read", can_approve_pull_request_reviews=False
    )

    def check(self, context: RuleContext) -> RuleCheckResult:
        try:
            # Get the repository object
            repo = context.repository

            # Use the underlying API to get GitHub Actions default workflow permissions
            # GET /repos/{owner}/{repo}/actions/permissions/workflow
            url = f"/repos/{repo.owner.login}/{repo.name}/actions/permissions/workflow"
            response = repo._requester.requestJsonAndCheck("GET", url)
            permissions = response[1]

            permissions = DefaultWorkflowPermissionsRuleConfig.model_validate(
                permissions
            )

            if permissions != self.config:
                diff_lines = unified_diff(
                    self.config.model_dump_json(indent=2).splitlines(),
                    permissions.model_dump_json(indent=2).splitlines(),
                    fromfile="expected",
                    tofile="actual",
                    n=500,
                )
                diff = []
                for line in diff_lines:
                    if line.startswith("+"):
                        colored_line = f"[yellow]          {line}[/yellow]"
                    elif line.startswith("-"):
                        colored_line = f"[red]          {line}[/red]"
                    else:
                        colored_line = f"          {line}"
                    diff.append(colored_line)

                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="\n".join(
                        ["Wrong GitHub Actions default workflow permissions:"] + diff
                    ),
                    fix_available=True,
                    fix_description="Update GitHub Actions default workflow permissions.",
                )

            # All checks passed
            return RuleCheckResult(
                result=RuleResult.PASSED,
                message="GitHub Actions default workflow permissions are correctly configured.",
            )

        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check GitHub Actions default workflow permissions: {str(e)}",
                fix_available=False,
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        try:
            if context.dry_run:
                return (
                    True,
                    "Would update GitHub Actions default workflow permissions (dry run)",
                )

            repo = context.repository

            # PUT /repos/{owner}/{repo}/actions/permissions/workflow
            url = f"/repos/{repo.owner.login}/{repo.name}/actions/permissions/workflow"

            data = self.config.model_dump()

            repo._requester.requestJsonAndCheck("PUT", url, input=data)

            return (
                True,
                "Updated GitHub Actions default workflow permissions successfully.",
            )

        except GithubException as e:
            return (
                False,
                f"Failed to update GitHub Actions default workflow permissions: {str(e)}",
            )
