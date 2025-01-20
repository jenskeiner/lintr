"""Tests for rule and rule set base classes."""

from unittest.mock import MagicMock

import pytest

from repolint.rules import Rule, RuleCheckResult, RuleResult, RuleSet


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


def test_rule_set_add_duplicate_rule():
    """Test adding a duplicate rule to a rule set."""
    rule_set = RuleSet("RS001", "Test rule set")
    rule1 = DummyRule("R001", "Test rule 1", RuleResult.PASSED)
    rule2 = DummyRule("R001", "Test rule 2", RuleResult.FAILED)
    rule_set.add_rule(rule1)
    with pytest.raises(ValueError):
        rule_set.add_rule(rule2)


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


def test_rule_set_add_duplicate_rule_set():
    """Test adding a duplicate rule set."""
    parent_set = RuleSet("RS001", "Parent rule set")
    child_set1 = RuleSet("RS002", "Child rule set 1")
    child_set2 = RuleSet("RS002", "Child rule set 2")
    parent_set.add_rule_set(child_set1)
    with pytest.raises(ValueError):
        parent_set.add_rule_set(child_set2)
