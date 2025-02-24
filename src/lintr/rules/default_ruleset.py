"""Default rule set for Lintr."""

from lintr.rules.base import RuleSet
from lintr.rules.general import WebCommitSignoffRequiredEnabledRule
from lintr.rules.permission_rules import (
    SingleOwnerRule,
    NoCollaboratorsRule,
)
from lintr.rules.general import WikisDisabledRule, IssuesDisabledRule


def get_default_ruleset() -> RuleSet:
    """Create and return the default rule set.

    The default rule set contains a minimal set of rules that should be applied
    to all repositories by default. These rules check for basic repository
    hygiene and best practices.

    Returns:
        Default rule set instance.
    """
    rule_set = RuleSet(
        id="default",
        description="Default rule set with basic repository checks",
    )

    # Add basic repository checks
    rule_set.add_rule(WebCommitSignoffRequiredEnabledRule)
    rule_set.add_rule(SingleOwnerRule)
    rule_set.add_rule(NoCollaboratorsRule)
    rule_set.add_rule(WikisDisabledRule)
    rule_set.add_rule(IssuesDisabledRule)

    return rule_set
