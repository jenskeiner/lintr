"""Test fixtures and helper classes."""

from repolint.rules.base import Rule, RuleSet, RuleCheckResult, RuleResult
from repolint.rules.context import RuleContext
from repolint.rule_manager import RuleManager  # Import RuleManager


class TestRule(Rule):
    """Test rule implementation for testing."""

    def __init__(self, rule_id: str, description: str):
        super().__init__(rule_id, description)

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Always returns PASSED."""
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


class TestRuleSet(RuleSet):
    """Test rule set implementation for testing."""

    def __init__(self, rule_set_id: str, description: str, rules: list = None):
        super().__init__(rule_set_id, description)
        if rules is None:
            # Default rules
            self.add_rule(TestRule("R001", "Test rule 1"))
            self.add_rule(TestRule("R002", "Test rule 2"))
        else:
            # Add custom rules from rule IDs
            rule_manager = RuleManager()
            for rule_id in rules:
                rule = rule_manager.get_all_rules().get(rule_id)
                if rule:
                    self.add_rule(rule)
