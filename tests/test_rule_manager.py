"""Tests for the Rule Manager singleton."""

from unittest.mock import patch, MagicMock
import pytest

from repolint.rule_manager import RuleManager
from repolint.rules import Rule, RuleSet


class DummyRule(Rule):
    """Dummy rule for testing."""
    
    def check(self, repo):
        return None
        
    def can_fix(self):
        return False
        
    def fix(self, repo):
        return False


class DummyRuleSet(RuleSet):
    """Dummy rule set for testing."""
    
    def __init__(self):
        super().__init__("RS999", "Test Rule Set")


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton state before each test."""
    RuleManager._instance = None
    RuleManager._initialized = False
    yield


def test_singleton_behavior():
    """Test that RuleManager behaves as a singleton."""
    manager1 = RuleManager()
    manager2 = RuleManager()
    assert manager1 is manager2


def test_rule_discovery():
    """Test that rules are properly discovered from entry points."""
    # Mock entry points
    mock_entry_point = MagicMock()
    mock_entry_point.name = 'test_rule'
    mock_entry_point.load.return_value = DummyRule
    
    with patch('importlib.metadata.entry_points') as mock_entry_points:
        mock_entry_points.return_value = [mock_entry_point]
        manager = RuleManager()
        
        # Verify rule discovery
        rule_ids = manager.get_all_rule_ids()
        assert len(rule_ids) == 1
        assert "TEMP" in rule_ids


def test_rule_set_discovery():
    """Test that rule sets are properly discovered from entry points."""
    # Mock entry points
    dummy_rule_set = DummyRuleSet()
    mock_entry_point = MagicMock()
    mock_entry_point.name = 'test_rule_set'
    mock_entry_point.load.return_value = dummy_rule_set
    
    with patch('importlib.metadata.entry_points') as mock_entry_points:
        mock_entry_points.return_value = [mock_entry_point]
        manager = RuleManager()
        
        # Verify rule set discovery
        rule_set_ids = manager.get_all_rule_set_ids()
        assert len(rule_set_ids) == 1
        assert "RS999" in rule_set_ids


def test_rule_creation():
    """Test creating rule instances."""
    manager = RuleManager()
    
    # Register a dummy rule
    manager._rules["R999"] = DummyRule
    
    # Try creating a rule instance
    rule = manager.create_rule("R999", "Test Description")
    assert rule is not None
    assert isinstance(rule, DummyRule)
    assert rule.rule_id == "R999"
    assert rule.description == "Test Description"


def test_nonexistent_rule():
    """Test behavior with nonexistent rule IDs."""
    manager = RuleManager()
    
    # Try getting a nonexistent rule
    assert manager.get_rule_class("NONEXISTENT") is None
    
    # Try creating a nonexistent rule
    assert manager.create_rule("NONEXISTENT", "Test") is None


def test_invalid_entry_point():
    """Test handling of invalid entry points."""
    # Mock entry points with one that raises an exception
    mock_entry_point = MagicMock()
    mock_entry_point.name = 'invalid_rule'
    mock_entry_point.load.side_effect = ImportError("Test error")
    
    with patch('importlib.metadata.entry_points') as mock_entry_points:
        mock_entry_points.return_value = [mock_entry_point]
        manager = RuleManager()
        
        # Verify no rules were loaded
        assert len(manager.get_all_rule_ids()) == 0
