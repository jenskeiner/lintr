"""Tests for rule and rule set base classes."""

from unittest.mock import MagicMock

import pytest

from repolint.rules import Rule, RuleCheckResult, RuleResult, RuleSet
from repolint.rules.context import RuleContext

class DummyRule(Rule):
    """Dummy rule implementation for testing."""

    def __init__(self, rule_id: str, description: str, result: RuleResult):
        super().__init__(rule_id, description)
        self._result = result

    def check(self, repo) -> RuleCheckResult:
        """Return predefined result."""
        return RuleCheckResult(
            result=self._result,
            message=f"Rule {self.rule_id} returned {self._result.value}"
        )

    def can_fix(self) -> bool:
        """This dummy rule cannot fix anything."""
        return False

    def fix(self, repo) -> bool:
        """This dummy rule cannot fix anything."""
        return False

class MutuallyExclusiveRule1(Rule):
    """Test rule that is mutually exclusive with Rule2."""
    
    mutually_exclusive_with = {"R002"}  # Class-level declaration
    
    def __init__(self):
        super().__init__("R001", "Test Rule 1")
    
    def check(self, context: RuleContext) -> RuleCheckResult:
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


class MutuallyExclusiveRule2(Rule):
    """Test rule that is mutually exclusive with Rule1."""
    
    mutually_exclusive_with = {"R001"}  # Class-level declaration
    
    def __init__(self):
        super().__init__("R002", "Test Rule 2")
    
    def check(self, context: RuleContext) -> RuleCheckResult:
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


class BiDirectionalRule1(Rule):
    """Test rule that is mutually exclusive with Rule2 (bi-directional)."""
    mutually_exclusive_with = {"R002"}
    
    def __init__(self):
        super().__init__("R001", "Test Rule 1")
    
    def check(self, context: RuleContext) -> RuleCheckResult:
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


class BiDirectionalRule2(Rule):
    """Test rule that is mutually exclusive with Rule1 (bi-directional)."""
    mutually_exclusive_with = {"R001"}
    
    def __init__(self):
        super().__init__("R002", "Test Rule 2")
    
    def check(self, context: RuleContext) -> RuleCheckResult:
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


class OneDirectionalRule1(Rule):
    """Test rule that is mutually exclusive with Rule2 (one-directional)."""
    mutually_exclusive_with = {"R004"}
    
    def __init__(self):
        super().__init__("R003", "Test Rule 3")
    
    def check(self, context: RuleContext) -> RuleCheckResult:
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


class OneDirectionalRule2(Rule):
    """Test rule that Rule1 points to as mutually exclusive."""
    mutually_exclusive_with = set()  # Empty set, no explicit mutual exclusivity
    
    def __init__(self):
        super().__init__("R004", "Test Rule 4")
    
    def check(self, context: RuleContext) -> RuleCheckResult:
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


def test_rule_initialization():
    """Test basic rule initialization."""
    rule = DummyRule("R001", "Test rule", RuleResult.PASSED)
    assert rule.rule_id == "R001"
    assert rule.description == "Test rule"


def test_rule_check():
    """Test rule check functionality."""
    rule = DummyRule("R001", "Test rule", RuleResult.PASSED)
    mock_repo = MagicMock()
    result = rule.check(mock_repo)
    assert result.result == RuleResult.PASSED
    assert "Rule R001 returned passed" in result.message


def test_rule_set_initialization():
    """Test basic rule set initialization."""
    rule_set = RuleSet("RS001", "Test rule set")
    assert rule_set.rule_set_id == "RS001"
    assert rule_set.description == "Test rule set"
    assert len(list(rule_set.rules())) == 0


def test_rule_set_add_rule():
    """Test adding a rule to a rule set."""
    rule_set = RuleSet("RS001", "Test rule set")
    rule = DummyRule("R001", "Test rule", RuleResult.PASSED)
    rule_set.add_rule(rule)
    rules = list(rule_set.rules())
    assert len(rules) == 1
    assert rule in rules


def test_rule_set_add_rule_set():
    """Test adding a rule set to another rule set."""
    parent_set = RuleSet("RS001", "Parent rule set")
    child_set = RuleSet("RS002", "Child rule set")
    rule = DummyRule("R001", "Test rule", RuleResult.PASSED)
    child_set.add_rule(rule)
    parent_set.add_rule_set(child_set)
    rules = list(parent_set.rules())
    assert len(rules) == 1
    assert rule in rules


def test_rule_class_mutually_exclusive():
    """Test class-level mutually exclusive rules."""
    # Create instances of the rules
    rule1 = MutuallyExclusiveRule1()
    rule2 = MutuallyExclusiveRule2()
    rule3 = DummyRule("R003", "Test Rule 3", RuleResult.PASSED)

    # Test that class-level mutual exclusivity is respected
    assert "R002" in rule1.mutually_exclusive_with
    assert "R001" in rule2.mutually_exclusive_with

    # Verify other rules are not affected
    assert "R003" not in rule1.mutually_exclusive_with
    assert "R003" not in rule2.mutually_exclusive_with
    assert "R001" not in rule3.mutually_exclusive_with
    assert "R002" not in rule3.mutually_exclusive_with


def test_rule_class_mutually_exclusive_bi_directional():
    """Test bi-directional mutually exclusive rules."""
    rule1 = BiDirectionalRule1()
    rule2 = BiDirectionalRule2()

    # Both rules should see each other as mutually exclusive
    assert "R002" in rule1.mutually_exclusive_with
    assert "R001" in rule2.mutually_exclusive_with


def test_rule_class_mutually_exclusive_one_directional():
    """Test one-directional mutually exclusive rules."""
    rule1 = OneDirectionalRule1()
    rule2 = OneDirectionalRule2()

    # Rule1 sees Rule2 as mutually exclusive
    assert "R004" in rule1.mutually_exclusive_with
    # Rule2 doesn't explicitly mark Rule1 as mutually exclusive
    assert "R003" not in rule2.mutually_exclusive_with


def test_rule_set_preserves_order():
    """Test that rules and rule sets are returned in the order they were added."""
    # Create test rules with non-alphabetical IDs to ensure order is not by ID
    rule1 = DummyRule("R002", "Test Rule 2", RuleResult.PASSED)
    rule2 = DummyRule("R001", "Test Rule 1", RuleResult.PASSED)
    rule3 = DummyRule("R003", "Test Rule 3", RuleResult.PASSED)

    # Create test rule sets
    parent_set = RuleSet("RS001", "Parent Rule Set")
    child_set = RuleSet("RS002", "Child Rule Set")

    # Add rules in specific order
    parent_set.add_rule(rule1)  # R002
    parent_set.add_rule_set(child_set)
    child_set.add_rule(rule2)  # R001
    parent_set.add_rule(rule3)  # R003

    # Get all rules and verify order
    rules = list(parent_set.rules())
    assert len(rules) == 3
    assert rules[0].rule_id == "R002"  # First in parent set
    assert rules[1].rule_id == "R001"  # First in child set
    assert rules[2].rule_id == "R003"  # Last in parent set


def test_rule_set_effective_rules():
    """Test that effective_rules correctly handles mutually exclusive rules."""
    # Create a rule set with mutually exclusive rules
    rule_set = RuleSet("RS001", "Test rule set")
    
    # Add rules in order: R001, R002, R003, R004
    rule1 = OneDirectionalRule1()  # R003, excludes R004
    rule2 = OneDirectionalRule2()  # R004
    rule3 = BiDirectionalRule1()   # R001, excludes R002
    rule4 = BiDirectionalRule2()   # R002, excludes R001
    
    # Add rules in specific order to test both one-directional and bi-directional cases
    rule_set.add_rule(rule3)  # R001
    rule_set.add_rule(rule4)  # R002 (excludes R001)
    rule_set.add_rule(rule1)  # R003
    rule_set.add_rule(rule2)  # R004 (excluded by R003)
    
    # Get effective rules
    effective_rules = list(rule_set.effective_rules())
    
    # Should contain R002 (not R001 due to mutual exclusivity)
    # Should contain R003 (and not R004 due to one-directional exclusivity)
    assert len(effective_rules) == 2
    assert effective_rules[0].rule_id == "R002"
    assert effective_rules[1].rule_id == "R004"


def test_rule_set_effective_rules_nested():
    """Test that effective_rules correctly handles nested rule sets."""
    parent_set = RuleSet("RS001", "Parent rule set")
    child_set = RuleSet("RS002", "Child rule set")
    
    # Create rules with mutual exclusivity
    rule1 = BiDirectionalRule1()   # R001, excludes R002
    rule2 = BiDirectionalRule2()   # R002, excludes R001
    rule3 = OneDirectionalRule1()  # R003, excludes R004
    rule4 = OneDirectionalRule2()  # R004
    
    # Add rules to both parent and child sets
    parent_set.add_rule(rule1)  # R001
    child_set.add_rule(rule2)   # R002
    child_set.add_rule(rule3)   # R003
    parent_set.add_rule_set(child_set)
    parent_set.add_rule(rule4)  # R004
    
    # Get effective rules
    effective_rules = list(parent_set.effective_rules())
    
    # Should contain R002 (not R001 due to mutual exclusivity)
    # Should contain R003 (and not R004 due to one-directional exclusivity)
    assert len(effective_rules) == 2
    assert effective_rules[0].rule_id == "R002"
    assert effective_rules[1].rule_id == "R004"
