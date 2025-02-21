"""Tests for empty rule set."""

from lintr.rules.empty_ruleset import get_empty_ruleset


def test_empty_rule_set_init():
    """Test initialization of empty rule set."""
    rule_set = get_empty_ruleset()
    assert rule_set.id == "empty"
    assert "empty" in rule_set.description.lower()


def test_empty_rule_set_has_no_rules():
    """Test that empty rule set has no rules."""
    rule_set = get_empty_ruleset()
    assert len(list(rule_set.rules())) == 0
