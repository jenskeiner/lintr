"""Default rule set for Repolint."""

from repolint.rules.base import RuleSet
from repolint.rules.branch_rules import DefaultBranchExistsRule


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
        description="Default rule set with basic repository checks"
    )
    
    # Add basic repository checks
    rule_set.add_rule(DefaultBranchExistsRule())
    
    return rule_set
