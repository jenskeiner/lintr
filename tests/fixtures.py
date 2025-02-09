"""Test fixtures and helper classes."""

from abc import ABC
from collections.abc import Callable

from repolint.rule_manager import RuleManager  # Import RuleManager
from repolint.rules.base import Rule, RuleSet, RuleCheckResult, RuleResult
from repolint.rules.context import RuleContext


class TestRule(Rule, ABC):
    """Test rule implementation for testing."""

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Always returns PASSED."""
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


class TestRuleSet(RuleSet):
    """Test rule set implementation for testing."""

    class TestRule1(TestRule):
        _id = "R001"
        _description = "Test rule 1"

    class TestRule2(TestRule):
        _id = "R002"
        _description = "Test rule 2"

    def __init__(self, rule_set_id: str, description: str, rules: list = None):
        super().__init__(rule_set_id, description)
        if rules is None:
            # Default rules
            self.add_rule(TestRuleSet.TestRule1())
            self.add_rule(TestRuleSet.TestRule2())
        else:
            # Add custom rules from rule IDs
            rule_manager = RuleManager()
            for rule_id in rules:
                rule = rule_manager.get_all_rules().get(rule_id)
                if rule:
                    self.add_rule(rule)


def mk_rule(
    rule_id: str,
    description: str,
    result: RuleResult | RuleCheckResult | Exception | Callable = RuleCheckResult(
        RuleResult.PASSED, "Test passed"
    ),
    fix: Callable | None = None,
) -> type[Rule]:
    class R(Rule):
        _id = rule_id
        _description = description

        def check(self, context: RuleContext) -> RuleCheckResult:
            if isinstance(result, RuleResult):
                return RuleCheckResult(result, "Test passed")
            elif isinstance(result, RuleCheckResult):
                return result
            elif isinstance(result, Exception):
                raise result
            else:
                return result(context)

        def fix(self, context: RuleContext) -> tuple[bool, str]:
            if fix is not None:
                return fix(context)
            else:
                return super().fix(context)

    return R
