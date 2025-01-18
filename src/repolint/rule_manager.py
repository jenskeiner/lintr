"""Rule Manager singleton for discovering and managing rules and rule sets."""

import importlib.metadata
from typing import Dict, Optional, Set, Type, List

from repolint.rules import Rule, RuleSet
from repolint.rules.factories import RuleSetFactory
from repolint.config import BaseRepolintConfig


class RuleManager:
    """Singleton class for discovering and managing rules and rule sets."""

    _instance: Optional['RuleManager'] = None
    _initialized: bool = False

    def __new__(cls) -> 'RuleManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not RuleManager._initialized:
            self._rules: Dict[str, Type[Rule]] = {}
            self._rule_sets: Dict[str, RuleSet] = {}
            self._factory = RuleSetFactory()
            self._discover_rules()
            self._discover_rule_sets()
            
            RuleManager._initialized = True

    def _discover_rules(self) -> None:
        """Discover all available rules from entry points."""
        # In Python 3.13, entry_points() returns a dict-like object
        entry_points = importlib.metadata.entry_points()
        rule_entry_points = entry_points.select(group='repolint.rules')
        
        for entry_point in rule_entry_points:
            try:
                rule_class = entry_point.load()
                self._rules[entry_point.name] = rule_class
                self._factory.register_rule_class(entry_point.name, rule_class)
            except Exception as e:
                # Log warning about invalid entry point
                print(f"Warning: Failed to load rule {entry_point.name}: {e}")

    def _discover_rule_sets(self) -> None:
        """Discover all available rule sets from entry points."""
        # In Python 3.13, entry_points() returns a dict-like object
        entry_points = importlib.metadata.entry_points()
        rule_set_entry_points = entry_points.select(group='repolint.rule_sets')
        
        for entry_point in rule_set_entry_points:
            try:
                factory_func = entry_point.load()
                rule_set = factory_func()  # Call the factory function
                self._rule_sets[rule_set.rule_set_id] = rule_set
            except Exception as e:
                # Log warning about invalid entry point
                print(f"Warning: Failed to load rule set {entry_point.name}: {e}")

    def load_rule_sets_from_config(self, config: BaseRepolintConfig) -> None:
        """Load rule sets from configuration.
        
        Args:
            config: Repolint configuration.
            
        Raises:
            ValueError: If a rule set configuration is invalid.
        """
        # First pass: Create all rule sets with rules
        # This ensures all base rule sets exist before we try to add nested sets
        for rule_set_id, rule_set_config in config.rule_sets.items():
            if rule_set_id in self._rule_sets:
                print(f"Warning: Rule set {rule_set_id} already exists, skipping")
                continue
                
            if not rule_set_config.rules:
                continue
                
            try:
                rule_set = self.create_rule_set(
                    rule_set_id=rule_set_id,
                    description=rule_set_config.name,
                    rule_ids=rule_set_config.rules,
                )
                self._rule_sets[rule_set_id] = rule_set
            except ValueError as e:
                print(f"Error creating rule set {rule_set_id}: {e}")
                continue
        
        # Second pass: Create rule sets with nested sets
        for rule_set_id, rule_set_config in config.rule_sets.items():
            if rule_set_id in self._rule_sets or not rule_set_config.rule_sets:
                continue
                
            try:
                rule_set = self.create_rule_set(
                    rule_set_id=rule_set_id,
                    description=rule_set_config.name,
                )
                self._rule_sets[rule_set_id] = rule_set
            except ValueError as e:
                print(f"Error creating rule set {rule_set_id}: {e}")
                continue
        
        # Third pass: Add nested rule sets
        for rule_set_id, rule_set_config in config.rule_sets.items():
            if not rule_set_config.rule_sets:
                continue
                
            rule_set = self._rule_sets.get(rule_set_id)
            if not rule_set:
                continue
                
            has_valid_nested = False
            for nested_id in rule_set_config.rule_sets:
                nested_set = self._rule_sets.get(nested_id)
                if not nested_set:
                    print(f"Warning: Nested rule set {nested_id} not found for {rule_set_id}")
                    continue
                try:
                    rule_set.add_rule_set(nested_set)
                    has_valid_nested = True
                except ValueError as e:
                    print(f"Error adding nested rule set {nested_id} to {rule_set_id}: {e}")
            
            # If this rule set has no rules and no valid nested sets, remove it
            if not rule_set_config.rules and not has_valid_nested:
                del self._rule_sets[rule_set_id]

    def get_rule_class(self, rule_id: str) -> Optional[Type[Rule]]:
        """Get a rule class by its ID.
        
        Args:
            rule_id: ID of the rule to get.
            
        Returns:
            Rule class if found, None otherwise.
        """
        return self._rules.get(rule_id)

    def get_rule_set(self, rule_set_id: str) -> Optional[RuleSet]:
        """Get a rule set by its ID.
        
        Args:
            rule_set_id: ID of the rule set to get.
            
        Returns:
            Rule set if found, None otherwise.
        """
        return self._rule_sets.get(rule_set_id)

    def get_all_rule_ids(self) -> Set[str]:
        """Get all available rule IDs.
        
        Returns:
            Set of all rule IDs.
        """
        return set(self._rules.keys())

    def get_all_rule_set_ids(self) -> Set[str]:
        """Get all available rule set IDs.
        
        Returns:
            Set of all rule set IDs.
        """
        return set(self._rule_sets.keys())

    def create_rule(self, rule_id: str, description: str) -> Optional[Rule]:
        """Create a new instance of a rule.
        
        Args:
            rule_id: ID of the rule to create.
            description: Description for the new rule instance.
            
        Returns:
            New rule instance if the rule ID exists, None otherwise.
        """
        rule_class = self.get_rule_class(rule_id)
        if rule_class:
            return rule_class(rule_id, description)
        return None

    def create_rule_set(
        self,
        rule_set_id: str,
        description: str,
        rule_ids: Optional[List[str]] = None,
        nested_rule_set_ids: Optional[List[str]] = None,
    ) -> RuleSet:
        """Create a new rule set programmatically.
        
        Args:
            rule_set_id: ID for the new rule set.
            description: Description of what the rule set checks.
            rule_ids: Optional list of rule IDs to include.
            nested_rule_set_ids: Optional list of rule set IDs to include.
            
        Returns:
            New rule set with the specified rules.
            
        Raises:
            ValueError: If a rule ID is not registered.
        """
        rule_set = self._factory.create_rule_set(
            rule_set_id=rule_set_id,
            description=description,
            rule_ids=rule_ids,
            nested_rule_set_ids=nested_rule_set_ids,
        )
        self._rule_sets[rule_set_id] = rule_set
        return rule_set

    def get_all_rules(self) -> Dict[str, Rule]:
        """Get all available rules with their descriptions.
        
        Returns:
            Dictionary mapping rule IDs to rule instances with descriptions.
        """
        rules = {}
        for rule_id, rule_class in self._rules.items():
            rules[rule_id] = rule_class(rule_id, "")  # Description will be set by the rule class
        return rules

    def get_all_rule_sets(self) -> Dict[str, RuleSet]:
        """Get all available rule sets.
        
        Returns:
            Dictionary mapping rule set IDs to rule set instances.
        """
        return self._rule_sets.copy()
