"""Tests for rule set factories."""

import pytest

from repolint.rules.base import Rule, RuleCheckResult, RuleResult, RuleSet
from repolint.rules.context import RuleContext
from repolint.rules.factories import RuleSetFactory


class TestRule(Rule):
    """Test rule for testing."""

    def __init__(self):
        """Initialize the rule."""
        super().__init__(
            rule_id="TEST001",
            description="Test rule",
        )

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Always pass."""
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


def test_rule_set_factory_register_rule():
    """Test registering a rule class with the factory."""
    factory = RuleSetFactory()
    factory.register_rule_class("TEST001", TestRule)

    # Verify that registering the same rule ID twice raises an error
    with pytest.raises(ValueError):
        factory.register_rule_class("TEST001", TestRule)


def test_rule_set_factory_create_rule_set():
    """Test creating a rule set with the factory."""
    factory = RuleSetFactory()
    factory.register_rule_class("TEST001", TestRule)

    # Create a rule set with a single rule
    rule_set = factory.create_rule_set(
        rule_set_id="RS001",
        description="Test rule set",
        rule_ids=["TEST001"],
    )

    assert isinstance(rule_set, RuleSet)
    assert rule_set.rule_set_id == "RS001"
    assert rule_set.description == "Test rule set"
    assert len(list(rule_set.rules())) == 1

    # Verify that creating a rule set with an unknown rule ID raises an error
    with pytest.raises(ValueError):
        factory.create_rule_set(
            rule_set_id="RS002",
            description="Invalid rule set",
            rule_ids=["INVALID"],
        )
