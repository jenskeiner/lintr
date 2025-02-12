"""Rules package."""

from lintr.rules.base import Rule, RuleCheckResult, RuleResult, RuleSet
from lintr.rules.branch_rules import (
    DefaultBranchExistsRule,
    WebCommitSignoffRequiredRule,
)
from lintr.rules.permission_rules import SingleOwnerRule, NoCollaboratorsRule
from lintr.rules.general import PreserveRepositoryRule

__all__ = [
    "Rule",
    "RuleCheckResult",
    "RuleResult",
    "RuleSet",
    "DefaultBranchExistsRule",
    "WebCommitSignoffRequiredRule",
    "SingleOwnerRule",
    "NoCollaboratorsRule",
    "PreserveRepositoryRule",
]
