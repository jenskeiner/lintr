"""Base classes for rules and rule sets."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set

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

    def get_all_rules(self) -> Set[Rule]:
        """Get all rules in this rule set, including those from nested rule sets.
        
        Returns:
            Set of all unique rules.
        """
        rules = set(self._rules.values())
        for rule_set in self._rule_sets.values():
            rules.update(rule_set.get_all_rules())
        return rules

    def check_repository(self, repo: Repository) -> Dict[str, RuleCheckResult]:
        """Check a repository against all rules in this rule set.
        
        Args:
            repo: GitHub repository to check.
            
        Returns:
            Dictionary mapping rule IDs to their check results.
        """
        context = RuleContext(repository=repo)
        results = {}
        for rule in self.get_all_rules():
            results[rule.rule_id] = rule.check(context)
        return results
