"""Rule Manager singleton for discovering and managing rules and rule sets."""

import importlib.metadata
from typing import Optional
from collections.abc import Iterable

from lintr.rules import Rule, RuleSet
from lintr.config import CustomRuleDefinition, RuleSetConfig


class RuleManager:
    """Singleton class for discovering and managing rules and rule sets."""

    _instance: Optional["RuleManager"] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> "RuleManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance."""
        cls._instance = None
        cls._initialized = False

    def __init__(
        self,
        rules: dict[str, CustomRuleDefinition] | None = None,
        rulesets: dict[str, RuleSetConfig] | None = None,
    ) -> None:
        if rules is None:
            rules = {}
        if rulesets is None:
            rulesets = {}
        if not RuleManager._initialized:
            self._rules: dict[str, type[Rule] | RuleSet] = dict()
            self._discover_rules()
            self.add_rules(rules)
            self._discover_rule_sets()
            self.add_rulesets(rulesets)
            RuleManager._initialized = True

    def add_rule(self, rule_cls: type[Rule]) -> None:
        if rule_cls.rule_id in self._rules:
            raise ValueError(f"Rule {rule_cls.rule_id} already exists.")
        self._rules[rule_cls.rule_id] = rule_cls
        self._update_mutually_exclusive(rule_cls)

    def _discover_rules(self) -> None:
        """Discover all available rules from entry points."""
        # In Python 3.13, entry_points() returns a dict-like object
        entry_points = importlib.metadata.entry_points()
        rule_entry_points = entry_points.select(group="lintr.rules")

        for entry_point in rule_entry_points:
            try:
                # Load the rule class or factory
                rule_cls: type[Rule] = entry_point.load()
                self.add_rule(rule_cls)
            except Exception as e:
                raise ValueError(f"Failed to load rule {entry_point.name}.") from e

    def add_rules(
        self, rules: dict[str, CustomRuleDefinition] | Iterable[type[Rule]]
    ) -> None:
        if isinstance(rules, dict):
            for rule_id, rule_definition in rules.items():
                try:
                    # Lookup the base class.
                    base_cls = self._rules[rule_definition.base]
                    # Create a new sub-class of base.
                    rule_cls = type(
                        f"CustomRule{rule_id}",
                        (base_cls,),
                        {
                            "_id": rule_id,
                            "_description": rule_definition.description,
                            "_config": type(base_cls._config).model_validate(
                                rule_definition.config
                            ),
                        },
                    )
                    self.add_rule(rule_cls)
                except Exception as e:
                    raise ValueError(
                        f"Failed to create custom rule {rule_id}: {e}"
                    ) from e
        else:
            for rule in rules:
                self.add_rule(rule)

    def add_rule_set(self, ruleset: RuleSet) -> None:
        if ruleset.id in self._rules:
            raise ValueError(f"Rule or ruleset {ruleset.id} already exists.")
        self._rules[ruleset.id] = ruleset

    def _discover_rule_sets(self) -> None:
        """Discover all available rule sets from entry points."""
        # In Python 3.13, entry_points() returns a dict-like object
        entry_points = importlib.metadata.entry_points()
        rule_set_entry_points = entry_points.select(group="lintr.rule_sets")

        for entry_point in rule_set_entry_points:
            try:
                factory_func = entry_point.load()
                self.add_rule_set(factory_func())  # Call the factory function
            except Exception as e:
                # Log warning about invalid entry point
                raise ValueError(f"Failed to load ruleset {entry_point.name}.") from e

    def add_rulesets(
        self, rulesets: dict[str, RuleSetConfig] | Iterable[RuleSet]
    ) -> None:
        """Load rule sets from configuration.

        Args:
            config: Lintr configuration.

        Raises:
            ValueError: If a rule set configuration is invalid.
        """
        if isinstance(rulesets, dict):
            # First pass: Create all rule sets, but do not add any rules yet.
            # This ensures everything is in place before we add nested sets.
            for rule_set_id, rule_set_config in rulesets.items():
                if rule_set_id in self._rules:
                    raise ValueError(f"Rule or ruleset {rule_set_id} already exists")

                try:
                    rule_set = RuleSet(rule_set_id, rule_set_config.description)
                    # for r in rule_set_config.rules:
                    #     rule_set.add_rule(self.get_rule_class(r))
                    self._rules[rule_set_id] = rule_set
                except Exception as e:
                    raise ValueError(f"Error creating rule set {rule_set_id}.") from e

            # Second pass: Add rules and nested rulesets.
            for rule_set_id, rule_set_config in rulesets.items():
                rule_set = self._rules.get(rule_set_id)
                assert isinstance(rule_set, RuleSet)

                for nested_id in rule_set_config.rules:
                    try:
                        nested_set = self.get(nested_id)
                    except Exception as e:
                        raise ValueError(
                            f"Rule or ruleset {nested_id} not found for ruleset {rule_set_id}."
                        ) from e
                    try:
                        rule_set.add(nested_set)
                    except Exception as e:
                        raise ValueError(
                            f"Error adding rule or ruleset {nested_id} to ruleset {rule_set_id}: {e}"
                        ) from e
        else:
            for ruleset in rulesets:
                self.add_rule_set(ruleset)

    def get(self, id: str) -> type[Rule] | RuleSet:
        if id in self._rules:
            return self._rules[id]
        else:
            raise KeyError(f"Rule or rule set with ID {id} not found.")

    def get_all_rule_ids(self) -> set[str]:
        """Get all available rule IDs.

        Returns:
            Set of all rule IDs.
        """
        return {k for k, v in self._rules.items() if issubclass(v, Rule)}

    def get_all_rule_set_ids(self) -> set[str]:
        """Get all available rule set IDs.

        Returns:
            Set of all rule set IDs.
        """
        return {k for k, v in self._rules.items() if isinstance(v, RuleSet)}

    def get_all_rules(self) -> dict[str, type[Rule]]:
        """Get all available rules with their descriptions.

        Returns:
            Dictionary mapping rule IDs to rule instances with descriptions.
        """
        return {
            k: v
            for k, v in self._rules.items()
            if isinstance(v, type) and issubclass(v, Rule)
        }

    def get_all_rule_sets(self) -> dict[str, RuleSet]:
        """Get all available rule sets.

        Returns:
            Dictionary mapping rule set IDs to rule set instances.
        """
        return {k: v for k, v in self._rules.items() if isinstance(v, RuleSet)}

    def _update_mutually_exclusive(self, rule: type[Rule]):
        for id in rule._mutually_exclusive_with:
            other = self._rules.get(id)
            if other:
                rule._mutually_exclusive_with_resolved.add(other)
                other._mutually_exclusive_with_resolved.add(rule)
