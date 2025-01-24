"""Factories for creating rule sets programmatically."""


from repolint.rules.base import Rule, RuleSet


class RuleSetFactory:
    """Factory class for creating rule sets programmatically."""

    def __init__(self):
        """Initialize the rule set factory."""
        self._rule_classes: dict[str, type[Rule]] = {}

    def register_rule_class(self, rule_id: str, rule_class: type[Rule]) -> None:
        """Register a rule class for use in rule sets.

        Args:
            rule_id: ID to register the rule class under.
            rule_class: Rule class to register.

        Raises:
            ValueError: If a rule class with the same ID is already registered.
        """
        if rule_id in self._rule_classes:
            raise ValueError(f"Rule class with ID {rule_id} already registered")
        self._rule_classes[rule_id] = rule_class

    def create_rule_set(
        self,
        rule_set_id: str,
        description: str,
        rule_ids: list[str] | None = None,
        nested_rule_set_ids: list[str] | None = None,
    ) -> RuleSet:
        """Create a new rule set with the specified rules.

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
        rule_set = RuleSet(rule_set_id, description)

        # Add individual rules
        if rule_ids:
            for rule_id in rule_ids:
                rule_class = self._rule_classes.get(rule_id)
                if not rule_class:
                    raise ValueError(f"Rule class with ID {rule_id} not registered")
                rule = rule_class(
                    rule_id, rule_class.__doc__ or "No description available"
                )
                rule_set.add_rule(rule)

        # Add nested rule sets
        if nested_rule_set_ids:
            from repolint.rule_manager import RuleManager

            rule_manager = RuleManager()
            for nested_id in nested_rule_set_ids:
                nested_set = rule_manager.get_rule_set(nested_id)
                if not nested_set:
                    raise ValueError(f"Rule set with ID {nested_id} not found")
                rule_set.add_rule_set(nested_set)

        return rule_set
