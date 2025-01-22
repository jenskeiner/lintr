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

        self._items.append(rule)

    def add_rule_set(self, rule_set: 'RuleSet') -> None:
        """Add another rule set to this rule set.
        
        Args:
            rule_set: Rule set to add.
            
        Raises:
            ValueError: If a rule set with the same ID already exists.
        """
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

    def effective_rules(self) -> Iterator[Rule]:
        """Get all rules in this rule set with mutually exclusive rules removed.
        
        Rules are processed in reverse order (last added first). For each rule,
        any mutually exclusive rules that occur earlier in the list are removed.
        
        Yields:
            Rules in order, with mutually exclusive rules removed.
        """
        
        # Get all rules as a list first
        all_rules = list(self.rules())

        # Build up a dictionary of mutually exclusive rules.
        mutually_exclusive_rules = dict()
        for rule in all_rules:
            for id in rule.mutually_exclusive_with:
                mutually_exclusive_rules[rule.rule_id] = mutually_exclusive_rules.get(rule.rule_id, set()) | {id}
                mutually_exclusive_rules[id] = mutually_exclusive_rules.get(id, set()) | {rule.rule_id}

        def filter_exclusive_rules(rules: List[Rule]) -> Iterator[Rule]:
            """Filter out mutually exclusive rules.
            
            For each rule (processed from the end), removes any earlier rules
            that are mutually exclusive with it.
            
            Args:
                rules: List of rules to filter
                
            Yields:
                Rules with mutually exclusive ones removed
            """
            excluded_rules = set()  # Track which rules to exclude
            
            # Process rules from end to start
            for rule in reversed(rules):
                if rule.rule_id in excluded_rules:
                    continue
                    
                # Include this rule and mark its mutually exclusive rules for exclusion
                excluded_rules.update(mutually_exclusive_rules.get(rule.rule_id, set()))
                yield rule
                
        # Filter out mutually exclusive rules and reverse back to original order
        yield from reversed(list(filter_exclusive_rules(all_rules)))