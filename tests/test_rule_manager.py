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
    default_ruleset = RuleSet("default", "Default rule set")

    mock_entry_point1 = MagicMock()
    mock_entry_point1.name = "test_rule_set"
    mock_entry_point1.load.return_value = lambda: dummy_rule_set

    mock_entry_point2 = MagicMock()
    mock_entry_point2.name = "default"
    mock_entry_point2.load.return_value = lambda: default_ruleset

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


def test_rule_manager_load_valid_rule_sets(manager):
    """Test loading valid rule sets from configuration."""
    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value.select.return_value = []

        # Create a config with valid rule sets
        config = BaseLintrConfig(
            github_token="dummy",
            rulesets={
                "RS001": RuleSetConfig(
                    description="Test rule set 1",
                    rules=["TEST001"],
                ),
            },
        )

        # Load rule sets from config
        manager.add_rulesets(config.rulesets)

        # Verify that valid rule sets were created
        rs001 = manager.get("RS001")
        assert rs001 is not None
        assert isinstance(rs001, RuleSet)
        assert rs001.id == "RS001"
        assert rs001.description == "Test rule set 1"
        assert len(list(rs001.rules())) == 1


def test_rule_manager_load_valid_nested_rule_sets(manager):
    """Test loading valid rule sets with nested rule sets from configuration."""
    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value.select.return_value = []

        # Create a config with nested rule sets
        config = BaseLintrConfig(
            github_token="dummy",
            rulesets={
                "RS001": RuleSetConfig(
                    description="Test rule set 1",
                    rules=["TEST001"],
                ),
                "RS002": RuleSetConfig(
                    description="Test rule set 2",
                    rules=["RS001"],  # Nested rule set
                ),
            },
        )

        # Load rule sets from config
        manager.add_rulesets(config.rulesets)

        # Verify that nested rule set was created
        rs002 = manager.get("RS002")
        assert rs002 is not None
        assert isinstance(rs002, RuleSet)
        assert rs002.id == "RS002"
        assert rs002.description == "Test rule set 2"
        assert len(list(rs002.rules())) == 1  # Inherits rule from RS001


def test_rule_manager_load_invalid_rule_references(manager):
    """Test that loading rule sets with invalid rule references raises an exception."""
    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value.select.return_value = []

        # Create a config with invalid rule references
        config = BaseLintrConfig(
            github_token="dummy",
            rulesets={
                "RS001": RuleSetConfig(
                    description="Test rule set 1",
                    rules=["INVALID"],  # Invalid rule ID
                ),
            },
        )

        # Loading rule sets with invalid rule references should raise ValueError
        with pytest.raises(
            ValueError, match=r"Rule or ruleset INVALID not found for ruleset RS001"
        ):
            manager.add_rulesets(config.rulesets)


def test_rule_manager_load_invalid_nested_rule_sets(manager):
    """Test that loading rule sets with invalid nested rule set references raises an exception."""
    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value.select.return_value = []

        # Create a config with invalid nested rule set references
        config = BaseLintrConfig(
            github_token="dummy",
            rulesets={
                "RS001": RuleSetConfig(
                    description="Test rule set 1",
                    rules=["INVALID"],  # Invalid nested rule set
                ),
            },
        )

        # Loading rule sets with invalid nested rule set references should raise ValueError
        with pytest.raises(
            ValueError, match=r"Rule or ruleset INVALID not found for ruleset RS001"
        ):
            manager.add_rulesets(config.rulesets)


def test_rule_manager_load_duplicate_rule_sets(manager):
    """Test that loading rule sets with duplicate IDs raises an exception."""
    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value.select.return_value = []

        # First, create a rule set
        config1 = BaseLintrConfig(
            github_token="dummy",
            rulesets={
                "RS001": RuleSetConfig(
                    description="Test rule set 1",
                    rules=["TEST001"],
                ),
            },
        )
        manager.add_rulesets(config1.rulesets)

        # Try to create another rule set with the same ID
        config2 = BaseLintrConfig(
            github_token="dummy",
            rulesets={
                "RS001": RuleSetConfig(
                    description="Test rule set 1 duplicate",
                    rules=["TEST001"],
                ),
            },
        )

        # Loading rule sets with duplicate IDs should raise ValueError
        with pytest.raises(ValueError, match=r"Rule or ruleset RS001 already exists"):
            manager.add_rulesets(config2.rulesets)


def test_rule_set_discovery_error_handling():
    """Test error handling during rule set discovery from entry points."""
    # Mock entry points
    mock_entry_point = MagicMock()
    mock_entry_point.name = "test_rule_set"
    mock_entry_point.load.side_effect = Exception("Failed to load rule set")

    with patch("importlib.metadata.entry_points") as mock_entry_points:

        def select(group):
            if group == "lintr.rule_sets":
                return [mock_entry_point]
            return []

        mock_entry_points.return_value.select = select

        with pytest.raises(
            ValueError, match=r"Failed to load ruleset test_rule_set"
        ):  # Should not raise exception, but log warning
            RuleManager()


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

        def select(group):
            if group == "lintr.rule_sets":
                return [
                    mock_entry_point_success,
                    mock_entry_point_failure,
                ]
            return []

        mock_entry_points.return_value.select = select

        with pytest.raises(
            ValueError, match=r"Failed to load ruleset test_rule_set_failure"
        ):  # Should not raise exception, but log warning
            RuleManager()


def test_rule_discovery_error_handling():
    """Test error handling during rule discovery from entry points."""
    # Mock entry points
    mock_entry_point = MagicMock()
    mock_entry_point.name = "test_rule"
    mock_entry_point.load.side_effect = Exception("Failed to load rule")

    with patch("importlib.metadata.entry_points") as mock_entry_points:

        def select(group):
            if group == "lintr.rules":
                return [mock_entry_point]
            return []

        mock_entry_points.return_value.select = select

        with pytest.raises(ValueError, match=r"Failed to load rule test_rule"):
            RuleManager()


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

        def select(group):
            if group == "lintr.rules":
                return [
                    mock_entry_point_success,
                    mock_entry_point_failure,
                ]
            return []

        mock_entry_points.return_value.select = select

        with pytest.raises(ValueError, match=r"Failed to load rule test_rule_failure"):
            RuleManager()
