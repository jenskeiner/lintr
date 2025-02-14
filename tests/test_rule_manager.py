"""Tests for the rule manager."""

import pytest
from unittest.mock import MagicMock, patch

from lintr.rule_manager import RuleManager
from lintr.rules.base import Rule, RuleCheckResult, RuleResult, RuleSet
from lintr.rules.context import RuleContext
from lintr.config import BaseLintrConfig, RuleSetConfig


class TestRule(Rule):
    """Test rule for testing."""

    _id = "TEST001"
    _description = "Test rule"

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Always pass."""
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton state before each test."""
    RuleManager._instance = None
    RuleManager._initialized = False
    yield


@pytest.fixture
def manager():
    manager = RuleManager()

    # Register a rule class
    manager._rules[TestRule.rule_id] = TestRule
    manager._factory.register_rule_class(TestRule.rule_id, TestRule)

    return manager


def test_rule_manager_singleton():
    """Test that RuleManager is a singleton."""
    with patch("importlib.metadata.entry_points") as mock_entry_points:
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
    mock_entry_point1.name = "test_rule_set"
    mock_entry_point1.load.return_value = lambda: dummy_rule_set

    mock_entry_point2 = MagicMock()
    mock_entry_point2.name = "default"
    mock_entry_point2.load.return_value = lambda: default_rule_set

    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value.select.side_effect = lambda group: {
            "lintr.rules": [],
            "lintr.rule_sets": [mock_entry_point1, mock_entry_point2],
        }[group]

        manager = RuleManager()

        # Verify rule set discovery
        rule_set_ids = manager.get_all_rule_set_ids()
        assert len(rule_set_ids) == 2
        assert "default" in rule_set_ids
        assert "RS999" in rule_set_ids


def test_rule_manager_load_rule_sets_from_config(manager):
    """Test loading rule sets from configuration."""
    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value.select.return_value = []

        # Create a config with rule sets
        config = BaseLintrConfig(
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
        assert rs001.id == "RS001"
        assert rs001.description == "Test rule set 1"
        assert len(list(rs001.rules())) == 1

        # Verify that nested rule set was created
        rs002 = manager.get_rule_set("RS002")
        assert rs002 is not None
        assert rs002.id == "RS002"
        assert rs002.description == "Test rule set 2"
        assert len(list(rs002.rules())) == 1  # Inherits rule from RS001

        # Verify that invalid rule sets were skipped
        assert manager.get_rule_set("RS003") is None
        assert manager.get_rule_set("RS004") is None


def test_rule_manager_create_rule_set(manager):
    """Test creating a rule set with the rule manager."""
    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value.select.return_value = []

        # Create a rule set with a single rule
        rule_set = manager.create_rule_set(
            rule_set_id="RS001",
            description="Test rule set",
            rule_ids=["TEST001"],
        )

        assert isinstance(rule_set, RuleSet)
        assert rule_set.id == "RS001"
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


def test_rule_set_discovery_error_handling():
    """Test error handling during rule set discovery from entry points."""
    # Mock entry points
    mock_entry_point = MagicMock()
    mock_entry_point.name = "test_rule_set"
    mock_entry_point.load.side_effect = Exception("Failed to load rule set")

    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value.select.return_value = [mock_entry_point]

        # Should not raise exception, but log warning
        manager = RuleManager()

        # Verify rule set was not registered
        assert "test_rule_set" not in manager._rule_sets


def test_rule_set_discovery_mixed_success():
    """Test rule set discovery with mix of successful and failed entry points."""
    # Mock entry points
    dummy_rule_set = RuleSet("RS999", "Test rule set")

    mock_entry_point_success = MagicMock()
    mock_entry_point_success.name = "test_rule_set_success"
    mock_entry_point_success.load.return_value = lambda: dummy_rule_set

    mock_entry_point_failure = MagicMock()
    mock_entry_point_failure.name = "test_rule_set_failure"
    mock_entry_point_failure.load.side_effect = Exception("Failed to load rule set")

    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value.select.return_value = [
            mock_entry_point_success,
            mock_entry_point_failure,
        ]

        # Should not raise exception
        manager = RuleManager()

        # Verify successful rule set was registered
        assert dummy_rule_set.id in manager._rule_sets

        # Verify failed rule set was not registered
        assert "test_rule_set_failure" not in manager._rule_sets


def test_rule_set_config_validation(manager):
    """Test validation of rule set configurations."""
    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value.select.return_value = []

        # Create a config with various edge cases
        config = BaseLintrConfig(
            github_token="dummy",
            rule_sets={
                # Empty rule set with no rules or nested sets
                "RS001": RuleSetConfig(
                    name="Empty rule set",
                    rules=[],
                    rule_sets=[],
                ),
                # Rule set with invalid nested set reference
                "RS002": RuleSetConfig(
                    name="Invalid nested set",
                    rule_sets=["NONEXISTENT"],
                ),
                # Valid rule set that will be referenced
                "RS003": RuleSetConfig(
                    name="Valid rule set",
                    rules=["TEST001"],
                ),
                # Rule set with mix of valid and invalid nested sets
                "RS004": RuleSetConfig(
                    name="Mixed nested sets",
                    rule_sets=["RS003", "NONEXISTENT"],
                ),
                # Rule set with only rules, no nested sets
                "RS005": RuleSetConfig(
                    name="Rules only",
                    rules=["TEST001"],
                ),
                # Rule set with only nested sets, no rules
                "RS006": RuleSetConfig(
                    name="Nested only",
                    rule_sets=["RS005"],
                ),
            },
        )

        # Load rule sets from config
        manager.load_rule_sets_from_config(config)

        # Empty rule set should not be created
        assert manager.get_rule_set("RS001") is None

        # Rule set with only invalid nested set should not be created
        assert manager.get_rule_set("RS002") is None

        # Valid rule set should be created
        rs003 = manager.get_rule_set("RS003")
        assert rs003 is not None
        assert len(list(rs003.rules())) == 1

        # Rule set with mix of valid and invalid nested sets should be created
        # and include rules from valid nested set
        rs004 = manager.get_rule_set("RS004")
        assert rs004 is not None
        assert len(list(rs004.rules())) == 1  # Inherits rule from RS003

        # Rules only rule set should be created
        rs005 = manager.get_rule_set("RS005")
        assert rs005 is not None
        assert len(list(rs005.rules())) == 1

        # Nested only rule set should be created and inherit rules
        rs006 = manager.get_rule_set("RS006")
        assert rs006 is not None
        assert len(list(rs006.rules())) == 1  # Inherits rule from RS005


def test_rule_discovery_error_handling():
    """Test error handling during rule discovery from entry points."""
    # Mock entry points
    mock_entry_point = MagicMock()
    mock_entry_point.name = "test_rule"
    mock_entry_point.load.side_effect = Exception("Failed to load rule")

    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value.select.return_value = [mock_entry_point]

        # Should not raise exception, but log warning
        manager = RuleManager()

        # Verify rule was not registered
        assert "test_rule" not in manager._rules
        assert "test_rule" not in manager._factory._rule_classes


def test_rule_discovery_mixed_success():
    """Test rule discovery with mix of successful and failed entry points."""
    # Mock entry points
    mock_entry_point_success = MagicMock()
    mock_entry_point_success.name = "test_rule_success"

    # Create a custom rule class that will be registered
    class SuccessRule(Rule):
        _id = "TEST002"
        _description = "Success rule"

        def check(self, context: RuleContext) -> RuleCheckResult:
            return RuleCheckResult(RuleResult.PASSED, "Success")

    # Create a mock rule class that matches how rules are registered
    mock_entry_point_success.load.return_value = SuccessRule

    mock_entry_point_failure = MagicMock()
    mock_entry_point_failure.name = "test_rule_failure"
    mock_entry_point_failure.load.side_effect = Exception("Failed to load rule")

    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value.select.return_value = [
            mock_entry_point_success,
            mock_entry_point_failure,
        ]

        # Should not raise exception
        manager = RuleManager()

        # Verify successful rule was registered with its ID
        assert "TEST002" in manager._rules
        assert "TEST002" in manager._factory._rule_classes

        # Verify failed rule was not registered
        assert "test_rule_failure" not in manager._rules
        assert "test_rule_failure" not in manager._factory._rule_classes
