"""Tests for the default rule set."""

from repolint.rules.default_rule_set import get_default_rule_set
from repolint.rules.branch_rules import DefaultBranchExistsRule


def test_get_default_rule_set():
    """Test creating the default rule set."""
    rule_set = get_default_rule_set()
    
    assert rule_set.rule_set_id == "default"
    assert "Default rule set" in rule_set.description
    
    # Verify that the rule set contains all expected rules
    rules = list(rule_set.rules())
    assert len(rules) == 1
    assert isinstance(rules[0], DefaultBranchExistsRule)
