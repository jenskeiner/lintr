"""Tests for default rule set."""

from repolint.rules.default_rule_set import get_default_rule_set
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


def test_get_default_rule_set():
    """Test creating the default rule set."""
    rule_set = get_default_rule_set()

    assert rule_set.rule_set_id == "default"
    assert "Default rule set" in rule_set.description

    # Verify that the rule set contains all expected rules
    rules = list(rule_set.rules())
    assert len(rules) == 6

    # Verify that rules are in the expected order
    assert isinstance(rules[0], DefaultBranchExistsRule)
    assert isinstance(rules[1], WebCommitSignoffRequiredRule)
    assert isinstance(rules[2], SingleOwnerRule)
    assert isinstance(rules[3], NoCollaboratorsRule)
    assert isinstance(rules[4], WikisDisabledRule)
    assert isinstance(rules[5], IssuesDisabledRule)
