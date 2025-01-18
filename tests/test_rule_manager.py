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


def test_rule_manager_create_rule_set():
    """Test creating a rule set with the rule manager."""
    manager = RuleManager()
    
    # Register a rule class
    manager._rules["TEST001"] = DummyRule
    manager._factory.register_rule_class("TEST001", DummyRule)
    
    # Create a rule set with a single rule
    rule_set = manager.create_rule_set(
        rule_set_id="RS001",
        description="Test rule set",
        rule_ids=["TEST001"],
    )
    
    assert isinstance(rule_set, RuleSet)
    assert rule_set.rule_set_id == "RS001"
    assert rule_set.description == "Test rule set"
    assert len(list(rule_set.rules())) == 1
    
    # Verify that the rule set is registered
    assert manager.get_rule_set("RS001") is rule_set
    
    # Create a nested rule set
    nested_set = manager.create_rule_set(
        rule_set_id="RS002",
        description="Nested rule set",
        nested_rule_set_ids=["RS001"],
    )
    
    assert isinstance(nested_set, RuleSet)
    assert len(list(nested_set.rules())) == 1  # Inherits rule from RS001
    
    # Verify that creating a rule set with an unknown rule ID raises an error
    with pytest.raises(ValueError):
        manager.create_rule_set(
            rule_set_id="RS003",
            description="Invalid rule set",
            rule_ids=["INVALID"],
        )
    
    # Verify that creating a rule set with an unknown nested rule set ID raises an error
    with pytest.raises(ValueError):
        manager.create_rule_set(
            rule_set_id="RS003",
            description="Invalid rule set",
            nested_rule_set_ids=["INVALID"],
        )


def test_rule_manager_load_rule_sets_from_config():
    """Test loading rule sets from configuration."""
    manager = RuleManager()
    
    # Register a rule class
    manager._rules["TEST001"] = DummyRule
    manager._factory.register_rule_class("TEST001", DummyRule)
    
    # Create a config with rule sets
    from repolint.config import BaseRepolintConfig, RuleSetConfig
    config = BaseRepolintConfig(
        github_token="dummy",
        rule_sets={
            "RS001": RuleSetConfig(
                name="Test rule set 1",
                rules=["TEST001"],
            ),
            "RS002": RuleSetConfig(
                name="Test rule set 2",
                rule_sets=["RS001"],  # Nested rule set
            ),
            "RS003": RuleSetConfig(
                name="Test rule set 3",
                rules=["INVALID"],  # Invalid rule ID
            ),
            "RS004": RuleSetConfig(
                name="Test rule set 4",
                rule_sets=["INVALID"],  # Invalid nested rule set
            ),
        },
    )
    
    # Load rule sets from config
    manager.load_rule_sets_from_config(config)
    
    # Verify that valid rule sets were created
    rs001 = manager.get_rule_set("RS001")
    assert rs001 is not None
    assert rs001.rule_set_id == "RS001"
    assert rs001.description == "Test rule set 1"
    assert len(list(rs001.rules())) == 1
    
    # Verify that nested rule set was created
    rs002 = manager.get_rule_set("RS002")
    assert rs002 is not None
    assert rs002.rule_set_id == "RS002"
    assert rs002.description == "Test rule set 2"
    assert len(list(rs002.rules())) == 1  # Inherits rule from RS001
    
    # Verify that invalid rule sets were skipped
    assert manager.get_rule_set("RS003") is None
    assert manager.get_rule_set("RS004") is None
