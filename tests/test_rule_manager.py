"""Tests for the rule manager."""

import pytest
from unittest.mock import MagicMock, patch

from repolint.rule_manager import RuleManager
from repolint.rules.base import Rule, RuleCheckResult, RuleResult, RuleSet
from repolint.rules.context import RuleContext
from repolint.config import BaseRepolintConfig, RuleSetConfig


class TestRule(Rule):
    """Test rule for testing."""
    
    def check(self, context: RuleContext) -> RuleCheckResult:
        """Always pass."""
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton state before each test."""
    RuleManager._instance = None
    RuleManager._initialized = False
    yield


def test_rule_manager_singleton():
    """Test that RuleManager is a singleton."""
    with patch('importlib.metadata.entry_points') as mock_entry_points:
        # Mock entry points to return empty collections
        mock_entry_points.return_value.select.return_value = []
        
        manager1 = RuleManager()
        manager2 = RuleManager()
        assert manager1 is manager2


def test_rule_set_discovery():
    """Test that rule sets are properly discovered from entry points."""
    # Mock entry points
    dummy_rule_set = RuleSet("RS999", "Test rule set")
    default_rule_set = RuleSet("default", "Default rule set")
    
    mock_entry_point1 = MagicMock()
    mock_entry_point1.name = 'test_rule_set'
    mock_entry_point1.load.return_value = lambda: dummy_rule_set
    
    mock_entry_point2 = MagicMock()
    mock_entry_point2.name = 'default'
    mock_entry_point2.load.return_value = lambda: default_rule_set
    
    with patch('importlib.metadata.entry_points') as mock_entry_points:
        mock_entry_points.return_value.select.side_effect = lambda group: {
            'repolint.rules': [],
            'repolint.rule_sets': [mock_entry_point1, mock_entry_point2],
        }[group]
        
        manager = RuleManager()
        
        # Verify rule set discovery
        rule_set_ids = manager.get_all_rule_set_ids()
        assert len(rule_set_ids) == 2
        assert "default" in rule_set_ids
        assert "RS999" in rule_set_ids


def test_rule_manager_default_rule_set():
    """Test that RuleManager creates the default rule set."""
    # Mock entry points
    default_rule_set = RuleSet("default", "Default rule set")
    mock_entry_point = MagicMock()
    mock_entry_point.name = 'default'
    mock_entry_point.load.return_value = lambda: default_rule_set
    
    with patch('importlib.metadata.entry_points') as mock_entry_points:
        mock_entry_points.return_value.select.side_effect = lambda group: {
            'repolint.rules': [],
            'repolint.rule_sets': [mock_entry_point],
        }[group]
        
        manager = RuleManager()
        
        # Verify that the default rule set exists
        default_set = manager.get_rule_set("default")
        assert default_set is not None
        assert default_set.rule_set_id == "default"
        assert "Default rule set" in default_set.description


def test_rule_manager_create_rule():
    """Test creating a rule with the rule manager."""
    with patch('importlib.metadata.entry_points') as mock_entry_points:
        mock_entry_points.return_value.select.return_value = []
        
        manager = RuleManager()
        # No rules registered yet
        with pytest.raises(ValueError):
            _ = manager.create_rule("TEST001", "Test rule")
        
        # Register a rule class
        manager._rules["TEST001"] = TestRule
        rule = manager.create_rule("TEST001", "Test rule")
        assert isinstance(rule, TestRule)
        assert rule.rule_id == "TEST001"
        assert rule.description == "Test rule"


def test_rule_manager_load_rule_sets_from_config():
    """Test loading rule sets from configuration."""
    with patch('importlib.metadata.entry_points') as mock_entry_points:
        mock_entry_points.return_value.select.return_value = []
        
        manager = RuleManager()
        
        # Register a rule class
        manager._rules["TEST001"] = TestRule
        manager._factory.register_rule_class("TEST001", TestRule)
        
        # Create a config with rule sets
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


def test_rule_manager_create_rule_set():
    """Test creating a rule set with the rule manager."""
    with patch('importlib.metadata.entry_points') as mock_entry_points:
        mock_entry_points.return_value.select.return_value = []
        
        manager = RuleManager()
        
        # Register a rule class
        manager._rules["TEST001"] = TestRule
        manager._factory.register_rule_class("TEST001", TestRule)
        
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
