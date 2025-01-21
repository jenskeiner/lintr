"""Base classes for rules and rule sets."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterator, Optional, Set, Tuple

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
        self._rules: Dict[str, Rule] = {}
        self._rule_sets: Dict[str, 'RuleSet'] = {}

    def add_rule(self, rule: Rule) -> None:
        """Add a rule to this rule set.
        
        Args:
            rule: Rule to add.
            
        Raises:
            ValueError: If a rule with the same ID already exists.
        """
        if rule.rule_id in self._rules:
            raise ValueError(f"Rule with ID {rule.rule_id} already exists")
        self._rules[rule.rule_id] = rule

    def add_rule_set(self, rule_set: 'RuleSet') -> None:
        """Add another rule set to this rule set.
        
        Args:
            rule_set: Rule set to add.
            
        Raises:
            ValueError: If a rule set with the same ID already exists.
        """
        if rule_set.rule_set_id in self._rule_sets:
            raise ValueError(f"Rule set with ID {rule_set.rule_set_id} already exists")
        self._rule_sets[rule_set.rule_set_id] = rule_set

    def rules(self) -> Iterator[Rule]:
        """Get all rules in this rule set, including those from nested rule sets.
        
        The rules are returned in order by their rule_id and duplicates are removed.
        If multiple rules have the same ID, only the first one encountered is included.
        
        Yields:
            Rules in this rule set and all nested rule sets, ordered by rule_id.
        """
        # Collect all rules in a dictionary to ensure uniqueness
        all_rules: Dict[str, Rule] = {}
        
        # Add rules from this rule set
        all_rules.update(self._rules)
        
        # Add rules from nested rule sets
        for rule_set in self._rule_sets.values():
            for rule in rule_set.rules():
                # Only add the rule if we haven't seen its ID before
                if rule.rule_id not in all_rules:
                    all_rules[rule.rule_id] = rule
        
        # Yield rules in order by rule_id
        for rule_id in sorted(all_rules.keys()):
            yield all_rules[rule_id]
