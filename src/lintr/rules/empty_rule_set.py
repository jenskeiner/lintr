"""Empty rule set for Lintr."""

from lintr.rules.base import RuleSet


def get_empty_rule_set() -> RuleSet:
    """Create and return an empty rule set.

    The empty rule set contains no rules and can be used as a starting point
    for creating custom rule sets or when no rules should be applied.

    Returns:
        Empty rule set instance.
    """
    rule_set = RuleSet(id="empty", description="Empty rule set with no rules")

    return rule_set
