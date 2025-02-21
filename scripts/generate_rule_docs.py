#!/usr/bin/env python3
"""Script to generate documentation for all lintr rules."""

from collections import defaultdict
from typing import get_args, get_origin

from lintr.rule_manager import RuleManager
from lintr.rules.base import Rule, BaseRuleConfig


def get_rule_parameter_class(rule_cls: type[Rule]) -> type[BaseRuleConfig]:
    """Extract the parameter class (ConfigT) from a Rule subclass.

    Args:
        rule_cls: The Rule subclass to analyze

    Returns:
        The parameter class used by this rule
    """
    # Look through the class's bases to find the Rule generic specialization
    for base in rule_cls.__orig_bases__:
        if (
            get_origin(base) is Rule
            and len(get_args(base)) == 1
            and issubclass(get_args(base)[0], BaseRuleConfig)
        ):
            return get_args(base)[0]

    # If we didn't find it in direct bases, check if the rule uses the default config
    if hasattr(rule_cls, "_config"):
        return type(rule_cls._config)

    return BaseRuleConfig


def collect_rules():
    """Collect all available rules and their parameter classes.

    Returns:
        A dictionary mapping category names to lists of (rule_class, param_class) tuples
    """
    # Initialize the rule manager to discover all rules
    rule_manager = RuleManager()

    # Group rules by their module for better organization
    rules_by_category = defaultdict(list)

    for rule_id, rule in rule_manager._rules.items():
        # Skip RuleSets, we only want Rule classes
        if not isinstance(rule, type) or not issubclass(rule, Rule):
            continue

        # Use the module name as category
        category = rule.__module__.split(".")[-1]
        param_class = get_rule_parameter_class(rule)
        rules_by_category[category].append((rule, param_class))

    return rules_by_category


def main():
    """Main entry point."""
    rules = collect_rules()

    # For now, just print what we found
    for category, rule_list in rules.items():
        print(f"\nCategory: {category}")
        for rule_cls, param_cls in rule_list:
            print(f"  Rule: {rule_cls._id} ({rule_cls.__name__})")
            print(f"    Description: {rule_cls._description}")
            print(f"    Parameters: {param_cls.__name__}")


if __name__ == "__main__":
    main()
