"""Base classes for rules and rule sets."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterator, List, Optional, Set, Tuple, Union

from github.Repository import Repository

from repolint.rules.context import RuleContext


class RuleResult(Enum):
    """Result of a rule check."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class RuleCheckResult:
    """Result of a rule check with details."""
    result: RuleResult
    message: str
    fix_available: bool = False
    fix_description: Optional[str] = None


class Rule(ABC):
    """Base class for all rules."""

    # Class-level set of rule IDs that this rule is mutually exclusive with
    mutually_exclusive_with: Set[str] = set()

    def __init__(self, rule_id: str, description: str):
        """Initialize a rule.
        
        Args:
            rule_id: Unique identifier for the rule (e.g., 'R001').
            description: Human-readable description of what the rule checks.
        """
        self.rule_id = rule_id
        self.description = description

    @abstractmethod
    def check(self, context: RuleContext) -> RuleCheckResult:
        """Check if the repository complies with this rule.
        
        Args:
            context: Context object containing all information needed for the check.
            
        Returns:
            Result of the check with details.
        """
        pass

    def fix(self, context: RuleContext) -> Tuple[bool, str]:
        """Apply the fix for this rule.
        
        This method should only be called if check() returned a RuleCheckResult
        with fix_available=True.
        
        Args:
            context: Context object containing all information needed for the fix.
            
        Returns:
            A tuple of (success, message) where success is a boolean indicating if
            the fix was successful, and message provides details about what was done
            or why the fix failed.
        """
        pass


class RuleSet:
    """A collection of rules that can be applied together."""

    def __init__(self, rule_set_id: str, description: str):
        """Initialize a rule set.
        
        Args:
            rule_set_id: Unique identifier for the rule set (e.g., 'RS001').
            description: Human-readable description of what the rule set checks.
        """
        self.rule_set_id = rule_set_id
        self.description = description
        # Store both rules and rule sets in a single list, maintaining order
        self._items: List[Union[Rule, 'RuleSet']] = []

    def add_rule(self, rule: Rule) -> None:
        """Add a rule to this rule set.
        
        Args:
            rule: Rule to add.
            
        Raises:
            ValueError: If a rule with the same ID already exists.
        """
        # Check for duplicates
        if any(isinstance(item, Rule) and item.rule_id == rule.rule_id 
               for item in self._items):
            raise ValueError(f"Rule {rule.rule_id} already exists in rule set")
        self._items.append(rule)

    def add_rule_set(self, rule_set: 'RuleSet') -> None:
        """Add another rule set to this rule set.
        
        Args:
            rule_set: Rule set to add.
            
        Raises:
            ValueError: If a rule set with the same ID already exists.
        """
        # Check for duplicates
        if any(isinstance(item, RuleSet) and item.rule_set_id == rule_set.rule_set_id 
               for item in self._items):
            raise ValueError(f"Rule set {rule_set.rule_set_id} already exists")
        self._items.append(rule_set)

    def rules(self) -> Iterator[Rule]:
        """Get all rules in this rule set, including those from nested rule sets.
        
        Rules are returned in the order they were added, with nested rule set rules 
        being inserted at the point where the rule set was added.
        
        Yields:
            Rules in this rule set and all nested rule sets in order of addition.
        """
        rules = []
        for item in self._items:
            if isinstance(item, Rule):
                rules.append(item)
            else:  # RuleSet
                rules.extend(item.rules())

        def remove_dupes(rules):
            seen = set()
            for rule in reversed(rules):
                if rule.rule_id not in seen:
                    seen.add(rule.rule_id)
                    yield rule
        
        rules = reversed(list(remove_dupes(rules)))

        yield from rules