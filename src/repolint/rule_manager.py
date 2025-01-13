"""Rule Manager singleton for discovering and managing rules and rule sets."""

import importlib.metadata
from typing import Dict, Optional, Set, Type

from repolint.rules import Rule, RuleSet


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
            self._discover_rules()
            self._discover_rule_sets()
            RuleManager._initialized = True

    def _discover_rules(self) -> None:
        """Auto-discover all rules via entry points."""
        for entry_point in importlib.metadata.entry_points(group='repolint.rules'):
            try:
                rule_class = entry_point.load()
                if (isinstance(rule_class, type) and 
                    issubclass(rule_class, Rule) and 
                    rule_class != Rule):
                    # Create an instance to get the rule_id
                    rule_instance = rule_class("TEMP", "Temporary instance for ID extraction")
                    self._rules[rule_instance.rule_id] = rule_class
            except Exception as e:
                # Log error but continue discovering other rules
                print(f"Error loading rule {entry_point.name}: {e}")

    def _discover_rule_sets(self) -> None:
        """Auto-discover all rule sets via entry points."""
        for entry_point in importlib.metadata.entry_points(group='repolint.rule_sets'):
            try:
                rule_set = entry_point.load()
                if isinstance(rule_set, RuleSet):
                    self._rule_sets[rule_set.rule_set_id] = rule_set
            except Exception as e:
                # Log error but continue discovering other rule sets
                print(f"Error loading rule set {entry_point.name}: {e}")

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
