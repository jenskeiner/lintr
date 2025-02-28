"""Rules for checking repository permission settings."""
import abc
from typing import Any

from colorama import Fore, Style
from difflib import unified_diff
from json import dumps

from github.GithubException import GithubException
from pydantic import Field

from lintr.rules.base import (
    Rule,
    RuleCheckResult,
    RuleResult,
    BaseRuleConfig,
    RuleCategory,
)
from lintr.rules.context import RuleContext


class SingleOwnerRule(Rule):
    """Rule that checks if the user is the only owner or admin of the repository."""

    _id = "R012"
    _description = "Repository must have only one owner or admin (the user)"

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

    _id = "R013"
    _description = "Repository must have no collaborators other than the user"

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


class NoClassicBranchProtectionRule(Rule):
    """Rule that checks if classic branch protection rules are used."""

    _id = "R019"
    _description = "Repository must not use classic branch protection rules"

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if classic branch protection rules are used.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        try:
            # Get all branches
            branches = context.repository.get_branches()

            # Check each branch for classic branch protection
            protected_branches = []
            for branch in branches:
                if branch.protected:
                    try:
                        # Get protection settings to check if they are classic rules
                        protection = branch.get_protection()
                        # Classic protection has no required_status_checks and no required_pull_request_reviews
                        if (
                            protection.required_status_checks is None
                            and protection.required_pull_request_reviews is None
                        ):
                            protected_branches.append(branch.name)
                    except GithubException as e0:
                        if (
                            e0.status != 404
                            or e0.data.get("message") != "Branch not protected"
                        ):
                            raise

            if not protected_branches:
                return RuleCheckResult(
                    result=RuleResult.PASSED,
                    message="No classic branch protection rules found",
                )
            else:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message=f"Classic branch protection rules found on branches: {', '.join(protected_branches)}",
                    fix_available=True,
                    fix_description="Remove classic branch protection rules and replace with repository rules",
                )
        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check branch protection rules: {str(e)}",
                fix_available=False,
            )

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Apply the fix for this rule.

        Remove classic branch protection rules.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) indicating if the fix was successful.
        """
        try:
            # Get all branches
            branches = context.repository.get_branches()

            # Remove classic protection from each branch
            fixed_branches = []
            for branch in branches:
                if branch.protected:
                    protection = branch.get_protection()
                    # Classic protection has no required_status_checks and no required_pull_request_reviews
                    if (
                        protection.required_status_checks is None
                        and protection.required_pull_request_reviews is None
                    ):
                        branch.remove_protection()
                        fixed_branches.append(branch.name)

            if fixed_branches:
                return (
                    True,
                    f"Removed classic branch protection rules from branches: {', '.join(fixed_branches)}",
                )
            return True, "No classic branch protection rules found to remove"
        except GithubException as e:
            return False, f"Failed to remove classic branch protection rules: {str(e)}"


class BranchRulesetRuleConfig(BaseRuleConfig):
    name: str = Field(description="The name of the branch ruleset to check.")
    enabled: bool = Field(
        default=True, description="Whether the branch ruleset should be enabled."
    )
    included_refs: list[str] = Field(
        default_factory=list,
        description="List of refs to include in the branch ruleset.",
    )
    excluded_refs: list[str] = Field(
        default_factory=list,
        description="List of refs to exclude from the branch ruleset.",
    )
    bypass_actors: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of actors that should bypass the branch ruleset.",
    )
    rules: dict[str, dict[str, Any] | None] = Field(
        default_factory=dict,
        description="List of required rules for the branch ruleset.",
    )


class BranchRulesetRule(Rule[BranchRulesetRuleConfig], abc.ABC):
    _id = "M001"
    _category = RuleCategory.MISC
    _description = "Checks that a ruleset with given properties exists."
    _example = BranchRulesetRuleConfig(
        name="ruleset",
        enabled=True,
        included_refs=["refs/heads/master"],
        excluded_refs=["refs/heads/develop"],
        bypass_actors=[
            {"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"}
        ],
        rules={
            "creation": None,
            "update": None,
            "deletion": None,
            "required_signatures": None,
            "pull_request": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews_on_push": True,
                "require_code_owner_review": True,
                "require_last_push_approval": True,
                "required_review_thread_resolution": True,
                "automatic_copilot_code_review_enabled": False,
                "allowed_merge_methods": ["merge"],
            },
            "non_fast_forward": None,
        },
    )

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if the branch has a proper branch ruleset set up.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        repo = context.repository
        try:
            # Get all rulesets for the repository
            rulesets = repo.get_rulesets()

            # Find the relevant ruleset
            ruleset = next((r for r in rulesets if r.name == self._config.name), None)

            if not ruleset:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message=f"No '{self._config.name}' ruleset found.",
                    fix_available=True,
                    fix_description=f"Create ruleset '{self._config.name}'.",
                )

            # Check ruleset configuration
            violations = []

            # Check if ruleset is enabled
            if ruleset.enforcement != "active":
                violations.append("Ruleset must be enabled.")

            # Check if ruleset applies exactly to branch
            ref_name_conditions = ruleset.conditions.get("ref_name", {})
            included_refs = list(ref_name_conditions.get("include", []))
            excluded_refs = list(ref_name_conditions.get("exclude", []))

            # Check included refs
            if set(included_refs) != set(self.config.included_refs):
                violations.append(
                    f"Ruleset includes refs {included_refs} but should include {self.config.included_refs}."
                )

            # Check excluded refs
            if set(excluded_refs) != set(self.config.excluded_refs):
                violations.append(
                    f"Ruleset excludes refs {excluded_refs} but should exclude {self.config.excluded_refs}."
                )

            # Check bypass actors.
            if ruleset.bypass_actors != self.config.bypass_actors:
                violations.append(
                    f"Ruleset bypass actors must be set to {self.config.bypass_actors}."
                )

            # Get the actual rules from the ruleset
            ruleset_rules = {rule.type: rule for rule in ruleset.rules}

            # Check for missing required rules.
            for rule_type, parameters_expected in self.config.rules.items():
                if rule_type not in ruleset_rules:
                    violations.append(f"Missing rule: {rule_type}")
                    continue
                rule = ruleset_rules[rule_type]
                if (
                    parameters_expected is not None
                    and rule.parameters != parameters_expected
                ):
                    diff = [
                        "          "
                        + (
                            f"{Fore.YELLOW}{x}{Style.RESET_ALL}"
                            if x.startswith("+")
                            else (
                                f"{Fore.RED}{x}{Style.RESET_ALL}"
                                if x.startswith("-")
                                else x
                            )
                        )
                        for x in unified_diff(
                            dumps(parameters_expected, indent=2).splitlines(),
                            dumps(rule.parameters, indent=2).splitlines(),
                            fromfile="expected",
                            tofile="actual",
                            n=500,
                        )
                    ]
                    violations.append(
                        "\n".join([f"Rule '{rule_type}' has wrong parameters: "] + diff)
                    )

            # Check for additional rules that are not required
            additional_rules = set(ruleset_rules.keys()) - set(self.config.rules.keys())
            if additional_rules:
                violations.append(
                    f"Additional rules found that are not allowed: {', '.join(sorted(additional_rules))}"
                )

            if violations:
                violations = [
                    f"Rulesset '{self._config.name}' not set up correctly:"
                ] + [f"      - {x}" for x in violations]

            return RuleCheckResult(
                result=RuleResult.PASSED if not violations else RuleResult.FAILED,
                message="\n".join(violations)
                if violations
                else f"Ruleset '{self._config.name}' properly configured",
                fix_available=bool(violations),
                fix_description=f"Update ruleset '{self._config.name}'."
                if violations
                else None,
            )

        except GithubException as e:
            if e.status == 404:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Repository rulesets not found",
                    fix_available=True,
                    fix_description=f"Create ruleset '{self._config.name}'.",
                )
            raise

    def fix(self, context: RuleContext) -> tuple[bool, str]:
        """Apply the fix for this rule.

        Create or update the branch ruleset with required settings.

        Args:
            context: Context object containing all information needed for the fix.

        Returns:
            A tuple of (success, message) indicating if the fix was successful.
        """
        try:
            # Get all branch rulesets
            rulesets = context.repository.get_rulesets()

            # Find existing ruleset targeting the branch
            ruleset = next((r for r in rulesets if r.name == self._config.name), None)

            # Define the ruleset configuration
            ruleset_config = {
                "name": self.config.name,
                "target": "branch",
                "enforcement": "active" if self.config.enabled else "inactive",
                "conditions": {
                    "ref_name": {
                        "include": self.config.included_refs,
                        "exclude": self.config.excluded_refs,
                    }
                },
                "bypass_actors": self._config.bypass_actors,
                "rules": [
                    {"type": k, "parameters": v} if v is not None else {"type": k}
                    for k, v in self._config.rules.items()
                ],
            }

            if ruleset:
                # Update existing ruleset
                ruleset.update(**ruleset_config)
                return (
                    True,
                    f"Updated ruleset '{self._config.name}'.",
                )
            else:
                # Create new ruleset
                context.repository.create_ruleset(**ruleset_config)
                return True, f"Created ruleset '{self._config.name}'."

        except GithubException as e:
            return False, f"Failed to fix branch ruleset: {str(e)}"
