"""Tests for default rule set."""

from lintr.rules.default_rule_set import get_default_rule_set
from lintr.rules.branch_rules import (
    DefaultBranchExistsRule,
    WebCommitSignoffRequiredRule,
)
from lintr.rules.permission_rules import (
    SingleOwnerRule,
    NoCollaboratorsRule,
    WikisDisabledRule,
    IssuesDisabledRule,
)


def test_get_default_rule_set():
    """Test creating the default rule set."""
    rule_set = get_default_rule_set()

    assert rule_set.id == "default"
    assert "Default rule set" in rule_set.description

    # Verify that the rule set contains all expected rules
    rules = list(rule_set.rules())
    assert len(rules) == 6

    # Verify that rules are in the expected order
    assert rules[0] is DefaultBranchExistsRule
    assert rules[1] is WebCommitSignoffRequiredRule
    assert rules[2] is SingleOwnerRule
    assert rules[3] is NoCollaboratorsRule
    assert rules[4] is WikisDisabledRule
    assert rules[5] is IssuesDisabledRule
