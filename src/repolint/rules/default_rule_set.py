"""Default rule set for Repolint."""

from repolint.rules.base import RuleSet
from repolint.rules.branch_rules import (
    DefaultBranchExistsRule,
    WebCommitSignoffRequiredRule,
)
from repolint.rules.permission_rules import (
    SingleOwnerRule,
    NoCollaboratorsRule,
    WikisDisabledRule,
    IssuesDisabledRule,
)


def get_default_rule_set() -> RuleSet:
    """Create and return the default rule set.

    The default rule set contains a minimal set of rules that should be applied
    to all repositories by default. These rules check for basic repository
    hygiene and best practices.

    Returns:
        Default rule set instance.
    """
    rule_set = RuleSet(
        rule_set_id="default",
        description="Default rule set with basic repository checks",
    )

    # Add basic repository checks
    rule_set.add_rule(DefaultBranchExistsRule())
    rule_set.add_rule(WebCommitSignoffRequiredRule())
    rule_set.add_rule(SingleOwnerRule())
    rule_set.add_rule(NoCollaboratorsRule())
    rule_set.add_rule(WikisDisabledRule())
    rule_set.add_rule(IssuesDisabledRule())

    return rule_set
