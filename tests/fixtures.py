"""Test fixtures and helper classes."""

from repolint.rules.base import Rule, RuleSet, RuleCheckResult, RuleResult
from repolint.rules.context import RuleContext


class TestRule(Rule):
    """Test rule implementation for testing."""
    
    def __init__(self, rule_id: str, description: str):
        super().__init__(rule_id, description)
    
    def check(self, context: RuleContext) -> RuleCheckResult:
        """Always returns PASSED."""
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


class TestRuleSet(RuleSet):
    """Test rule set implementation for testing."""
    
    def __init__(self, rule_set_id: str, description: str):
        super().__init__(rule_set_id, description)
        self.add_rule(TestRule("R001", "Test rule 1"))
        self.add_rule(TestRule("R002", "Test rule 2"))
