"""Tests for default rule set."""

from lintr.rules.default_ruleset import get_default_ruleset
from lintr.rules.general import WebCommitSignoffRequiredEnabledRule
from lintr.rules.permission_rules import (
    SingleOwnerRule,
    NoCollaboratorsRule,
)
from lintr.rules.general import WikisDisabledRule, IssuesDisabledRule


def test_get_default_ruleset():
    """Test creating the default rule set."""
    rule_set = get_default_ruleset()

    assert rule_set.id == "default"
    assert "Default rule set" in rule_set.description

    # Verify that the rule set contains all expected rules
    rules = list(rule_set.rules())
    assert len(rules) == 5

    # Verify that rules are in the expected order
    assert rules[0] is WebCommitSignoffRequiredEnabledRule
    assert rules[1] is SingleOwnerRule
    assert rules[2] is NoCollaboratorsRule
    assert rules[3] is WikisDisabledRule
    assert rules[4] is IssuesDisabledRule
