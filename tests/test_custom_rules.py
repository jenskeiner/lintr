"""Tests for custom rule functionality."""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import Field

from lintr.config import BaseLintrConfig, CustomRuleDefinition, RepositoryConfig
from lintr.rules.base import BaseRuleConfig, Rule, RuleCheckResult, RuleResult
from lintr.rules.context import RuleContext
from lintr.rule_manager import RuleManager


class DefaultBranchConfig(BaseRuleConfig):
    """Configuration for default branch rule."""

    allowed_names: list[str] = Field(default_factory=lambda: ["main", "master"])


class DefaultBranchRule(Rule[DefaultBranchConfig]):
    """Rule that checks if a repository has a default branch."""

    _id = "R001"
    _description = "Repository must have a default branch"
    _config = DefaultBranchConfig()

    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if the repository has a default branch.

        Args:
            context: Context object containing all information needed for the check.

        Returns:
            Result of the check with details.
        """
        default_branch = context.repository.default_branch
        if not default_branch:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message="Repository does not have a default branch",
                fix_available=False,
            )

        if default_branch not in self.config.allowed_names:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Default branch '{default_branch}' is not allowed. Must be one of: {', '.join(self.config.allowed_names)}",
                fix_available=False,
            )

        return RuleCheckResult(
            result=RuleResult.PASSED,
            message=f"Repository has allowed default branch: {default_branch}",
        )


class TestCustomRules:
    """Test suite for custom rule functionality."""

    @pytest.fixture
    def rule_manager(self):
        """Create a RuleManager with the test rule registered."""
        instance_old = RuleManager._instance
        RuleManager._instance = None
        initialized_old = RuleManager._initialized
        RuleManager._initialized = False

        with patch("importlib.metadata.entry_points") as mock_entry_points:
            # Mock entry points to return our test rule
            mock_entry_point = MagicMock()
            mock_entry_point.load.return_value = DefaultBranchRule
            mock_entry_points.return_value.select.return_value = [mock_entry_point]

            # Create manager and return
            manager = RuleManager()
            yield manager

        RuleManager._instance = instance_old
        RuleManager._initialized = initialized_old

    def test_custom_default_branch_rule(self, rule_manager):
        """Test custom rule inheriting from DefaultBranchExistsRule."""
        # Create a custom rule definition
        custom_rules = {
            "custom_branch": CustomRuleDefinition(
                base="R001",  # DefaultBranchExistsRule
                description="Custom branch rule",
                config={},
            )
        }

        # Initialize rule manager with custom rules
        rule_manager._add_custom_rules(custom_rules)

        # Create mock repository
        repo = MagicMock()
        repo.default_branch = "main"

        # Create context
        context = RuleContext(repository=repo)

        # Get and run the custom rule
        rule_cls = rule_manager.get_rule_class("custom_branch")
        assert rule_cls is not None, "Custom rule not found"

        rule = rule_cls()
        result = rule.check(context)

        # Verify results
        assert result.result == RuleResult.PASSED
        assert "main" in result.message

    def test_custom_rule_with_config(self, rule_manager):
        """Test custom rule with configuration override."""
        # Create a custom rule definition with config
        custom_rules = {
            "strict_branch": CustomRuleDefinition(
                base="R001",  # DefaultBranchExistsRule
                description="Strict branch rule",
                config={"allowed_names": ["master"]},  # Only allow master
            )
        }

        # Initialize rule manager with custom rules
        rule_manager._add_custom_rules(custom_rules)

        # Create mock repositories
        valid_repo = MagicMock()
        valid_repo.default_branch = "master"

        invalid_repo = MagicMock()
        invalid_repo.default_branch = "main"

        # Get the custom rule
        rule_cls = rule_manager.get_rule_class("strict_branch")
        assert rule_cls is not None, "Custom rule not found"

        rule = rule_cls()

        # Test with valid branch
        result = rule.check(RuleContext(repository=valid_repo))
        assert result.result == RuleResult.PASSED
        assert "master" in result.message

        # Test with invalid branch
        result = rule.check(RuleContext(repository=invalid_repo))
        assert result.result == RuleResult.FAILED
        assert "main" in result.message

    def test_repository_specific_config(self, rule_manager):
        """Test repository-specific configuration override."""
        # Create base custom rule
        custom_rules = {
            "configurable_branch": CustomRuleDefinition(
                base="R001",  # DefaultBranchExistsRule
                description="Configurable branch rule",
                config={"allowed_names": ["master", "main"]},
            )
        }

        # Create config with repository override
        config = BaseLintrConfig(
            github_token="test-token",
            rules=custom_rules,
            repository_rule_sets={
                "test/repo": RepositoryConfig(
                    ruleset="custom",
                    rules={"configurable_branch": {"allowed_names": ["develop"]}},
                )
            },
        )

        # Initialize rule manager
        rule_manager._add_custom_rules(config.rules)

        # Create mock repository
        repo = MagicMock()
        repo.default_branch = "develop"
        repo.full_name = "test/repo"

        # Get and run the custom rule
        rule_cls = rule_manager.get_rule_class("configurable_branch")
        assert rule_cls is not None, "Custom rule not found"

        # Create context with repository config
        context = RuleContext(
            repository=repo,
        )

        rule = rule_cls(
            type(rule_cls._config).model_validate(
                config.repository_rule_sets["test/repo"].rules["configurable_branch"]
            )
        )
        result = rule.check(context)

        # Verify that repository-specific config is used
        assert result.result == RuleResult.PASSED
        assert "develop" in result.message

    def test_custom_rule_in_ruleset(self, rule_manager):
        """Test using custom rules in a rule set."""
        # Create custom rules
        custom_rules = {
            "custom_branch1": CustomRuleDefinition(
                base="R001",
                description="Custom branch rule 1",
                config={},
            ),
            "custom_branch2": CustomRuleDefinition(
                base="R001",
                description="Custom branch rule 2",
                config={},
            ),
        }

        # Create config with rule set
        config = BaseLintrConfig(
            github_token="test-token",
            rules=custom_rules,
            rule_sets={
                "custom_set": {
                    "name": "Custom rule set",
                    "rules": ["custom_branch1", "custom_branch2"],
                }
            },
        )

        # Initialize rule manager and load rule sets
        rule_manager._add_custom_rules(config.rules)
        rule_manager.load_rule_sets_from_config(config)

        # Get the rule set
        rule_set = rule_manager.get_rule_set("custom_set")
        assert rule_set is not None, "Rule set not found"
        assert len(list(rule_set.rules())) == 2

        # Create mock repository
        repo = MagicMock()
        repo.default_branch = "main"

        # Create context
        context = RuleContext(repository=repo)

        # Run all rules in the set
        for rule in rule_set.rules():
            result = rule().check(context)
            assert result.result == RuleResult.PASSED
            assert "main" in result.message

    def test_invalid_custom_rule(self, rule_manager):
        """Test error handling for invalid custom rules."""
        # Try to create a custom rule with non-existent base
        custom_rules = {
            "invalid_rule": CustomRuleDefinition(
                base="NON_EXISTENT",
                description="Invalid rule",
                config={},
            )
        }

        # Verify that RuleManager raises an exception
        with pytest.raises(Exception) as exc_info:
            rule_manager._add_custom_rules(custom_rules)
        assert "Failed to create custom rule" in str(exc_info.value)

    def test_invalid_custom_rule_config(self, rule_manager):
        """Test error handling for invalid custom rule configuration."""
        # Try to create a custom rule with invalid config
        custom_rules = {
            "invalid_config": CustomRuleDefinition(
                base="R001",
                description="Rule with invalid config",
                config={"non_existent_field": "value"},
            )
        }

        # Verify that RuleManager raises an exception
        with pytest.raises(Exception) as exc_info:
            rule_manager._add_custom_rules(custom_rules)
        assert "Failed to create custom rule" in str(exc_info.value)
