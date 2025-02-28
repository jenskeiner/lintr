"""Tests for rule and rule set base classes."""

from unittest.mock import MagicMock

from abc import ABC
from lintr.rules import Rule, RuleCheckResult, RuleResult, RuleSet
from lintr.rules.context import RuleContext


class DummyRule(Rule, ABC):
    """Dummy rule implementation for testing."""

    def __init__(self, result: RuleResult):
        super().__init__()
        self._result = result

    def check(self, repo) -> RuleCheckResult:
        """Return predefined result."""
        return RuleCheckResult(
            result=self._result,
            message=f"Rule {self.rule_id} returned {self._result.value}",
        )

    def can_fix(self) -> bool:
        """This dummy rule cannot fix anything."""
        return False

    def fix(self, repo) -> bool:
        """This dummy rule cannot fix anything."""
        return False


class DummyRule1(DummyRule):
    _id = "G001"
    _description = "Test rule"


class MutuallyExclusiveRule1(Rule):
    """Test rule that is mutually exclusive with Rule2."""

    _id = "G001"
    _description = "Test Rule 1"
    _mutually_exclusive_with = {"G002"}  # Class-level declaration

    def check(self, context: RuleContext) -> RuleCheckResult:
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


class MutuallyExclusiveRule2(Rule):
    """Test rule that is mutually exclusive with Rule1."""

    _id = "G002"
    _description = "Test Rule 2"
    _mutually_exclusive_with = {"G001"}  # Class-level declaration

    def check(self, context: RuleContext) -> RuleCheckResult:
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


class OneDirectionalRule1(Rule):
    """Test rule that is mutually exclusive with Rule2 (one-directional)."""

    _id = "G003"
    _description = "Test Rule 3"
    _mutually_exclusive_with = {"G004"}

    def check(self, context: RuleContext) -> RuleCheckResult:
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


class OneDirectionalRule2(Rule):
    """Test rule that Rule1 points to as mutually exclusive."""

    _id = "G004"
    _description = "Test Rule 4"
    _mutually_exclusive_with = set()  # Empty set, no explicit mutual exclusivity

    def check(self, context: RuleContext) -> RuleCheckResult:
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


def test_rule_initialization():
    """Test basic rule initialization."""
    rule = DummyRule1(RuleResult.PASSED)
    assert rule.rule_id == "G001"
    assert rule.description == "Test rule"


def test_rule_check():
    """Test rule check functionality."""
    rule = DummyRule1(RuleResult.PASSED)
    mock_repo = MagicMock()
    result = rule.check(mock_repo)
    assert result.result == RuleResult.PASSED
    assert "Rule G001 returned passed" in result.message


def test_rule_set_initialization():
    """Test basic rule set initialization."""
    rule_set = RuleSet("RS001", "Test rule set")
    assert rule_set.id == "RS001"
    assert rule_set.description == "Test rule set"
    assert len(list(rule_set.rules())) == 0


def test_rule_set_add_rule(rule_cls):
    """Test adding a rule to a rule set."""
    rule_set = RuleSet("RS001", "Test rule set")
    rule = rule_cls("G001", "Test rule")
    rule_set.add(rule)
    rules = list(rule_set.rules())
    assert len(rules) == 1
    assert rule in rules


def test_rule_set_add_rule_set(rule_cls):
    """Test adding a rule set to another rule set."""
    parent_set = RuleSet("RS001", "Parent rule set")
    child_set = RuleSet("RS002", "Child rule set")
    rule = rule_cls("G001", "Test rule")
    child_set.add(rule)
    parent_set.add(child_set)
    rules = list(parent_set.rules())
    assert len(rules) == 1
    assert rule in rules


def test_rule_class_mutually_exclusive(rule_cls):
    """Test class-level mutually exclusive rules."""
    # Create instances of the rules
    rule1 = MutuallyExclusiveRule1()
    rule2 = MutuallyExclusiveRule2()
    rule3 = rule_cls("G003", "Test Rule 3", RuleResult.PASSED)()

    # Test that class-level mutual exclusivity is respected
    assert "G002" in rule1._mutually_exclusive_with
    assert "G001" in rule2._mutually_exclusive_with

    # Verify other rules are not affected
    assert "G003" not in rule1._mutually_exclusive_with
    assert "G003" not in rule2._mutually_exclusive_with
    assert "G001" not in rule3._mutually_exclusive_with
    assert "G002" not in rule3._mutually_exclusive_with


def test_rule_class_mutually_exclusive_bi_directional():
    """Test bi-directional mutually exclusive rules."""
    rule1 = MutuallyExclusiveRule1()
    rule2 = MutuallyExclusiveRule2()

    # Both rules should see each other as mutually exclusive
    assert "G002" in rule1._mutually_exclusive_with
    assert "G001" in rule2._mutually_exclusive_with


def test_rule_class_mutually_exclusive_one_directional():
    """Test one-directional mutually exclusive rules."""
    rule1 = OneDirectionalRule1()
    rule2 = OneDirectionalRule2()

    # Rule1 sees Rule2 as mutually exclusive
    assert "G004" in rule1._mutually_exclusive_with
    # Rule2 doesn't explicitly mark Rule1 as mutually exclusive
    assert "G003" not in rule2._mutually_exclusive_with


def test_rule_set_preserves_order(rule_cls):
    """Test that rules and rule sets are returned in the order they were added."""
    # Create test rules with non-alphabetical IDs to ensure order is not by ID
    rule1 = rule_cls("G002", "Test Rule 2", RuleResult.PASSED)
    rule2 = rule_cls("G001", "Test Rule 1", RuleResult.PASSED)
    rule3 = rule_cls("G003", "Test Rule 3", RuleResult.PASSED)

    # Create test rule sets
    parent_set = RuleSet("RS001", "Parent Rule Set")
    child_set = RuleSet("RS002", "Child Rule Set")

    # Add rules in specific order
    parent_set.add(rule1)  # G002
    parent_set.add(child_set)
    child_set.add(rule2)  # G001
    parent_set.add(rule3)  # G003

    # Get all rules and verify order
    rules = list(parent_set.rules())
    assert len(rules) == 3
    assert rules[0].rule_id == "G002"  # First in parent set
    assert rules[1].rule_id == "G001"  # First in child set
    assert rules[2].rule_id == "G003"  # Last in parent set


def test_rule_set_effective_rules():
    """Test that effective_rules correctly handles mutually exclusive rules."""
    # Create a rule set with mutually exclusive rules
    rule_set = RuleSet("RS001", "Test rule set")

    # Add rules in order: G001, G002, G003, G004
    rule1 = OneDirectionalRule1  # G003, excludes G004
    rule2 = OneDirectionalRule2  # G004
    rule3 = MutuallyExclusiveRule1  # G001, excludes G002
    rule4 = MutuallyExclusiveRule2  # G002, excludes G001

    # Add rules in specific order to test both one-directional and bi-directional cases
    rule_set.add(rule3)  # G001
    rule_set.add(rule4)  # G002 (excludes G001)
    rule_set.add(rule1)  # G003
    rule_set.add(rule2)  # G004 (excluded by G003)

    # Get effective rules
    effective_rules = list(rule_set.effective_rules())

    # Should contain G002 (not G001 due to mutual exclusivity)
    # Should contain G003 (and not G004 due to one-directional exclusivity)
    assert len(effective_rules) == 2
    assert effective_rules[0].rule_id == "G002"
    assert effective_rules[1].rule_id == "G004"


def test_rule_set_effective_rules_nested():
    """Test that effective_rules correctly handles nested rule sets."""
    parent_set = RuleSet("RS001", "Parent rule set")
    child_set = RuleSet("RS002", "Child rule set")

    # Create rules with mutual exclusivity
    rule1 = MutuallyExclusiveRule1  # G001, excludes G002
    rule2 = MutuallyExclusiveRule2  # G002, excludes G001
    rule3 = OneDirectionalRule1  # G003, excludes G004
    rule4 = OneDirectionalRule2  # G004

    # Add rules to both parent and child sets
    parent_set.add(rule1)  # G001
    child_set.add(rule2)  # G002
    child_set.add(rule3)  # G003
    parent_set.add(child_set)
    parent_set.add(rule4)  # G004

    # Get effective rules
    effective_rules = list(parent_set.effective_rules())

    # Should contain G002 (not G001 due to mutual exclusivity)
    # Should contain G003 (and not G004 due to one-directional exclusivity)
    assert len(effective_rules) == 2
    assert effective_rules[0].rule_id == "G002"
    assert effective_rules[1].rule_id == "G004"
