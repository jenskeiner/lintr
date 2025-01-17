"""Core linting functionality for Repolint."""

from typing import Dict, List, Optional, Tuple

from github.Repository import Repository

from repolint.config import BaseRepolintConfig
from repolint.rule_manager import RuleManager
from repolint.rules import RuleSet
from repolint.rules.context import RuleContext


class Linter:
    """Core linting functionality."""

    def __init__(self, config: BaseRepolintConfig, dry_run: bool = False):
        """Initialize the linter.
        
        Args:
            config: Repolint configuration.
            dry_run: If True, no changes will be made.
        """
        self._config = config
        self._dry_run = dry_run
        self._rule_manager = RuleManager()

    def create_context(self, repository: Repository) -> RuleContext:
        """Create a rule context for a repository.
        
        Args:
            repository: GitHub repository to create context for.
            
        Returns:
            Rule context for the repository.
        """
        return RuleContext(repository=repository)

    def get_rule_set_for_repository(self, repository: Repository) -> Optional[Tuple[str, RuleSet]]:
        """Get the rule set to use for a repository.
        
        The rule set is determined in the following order:
        1. Repository-specific rule set from configuration
        2. Default rule set from configuration
        
        Args:
            repository: GitHub repository to get rule set for.
            
        Returns:
            Tuple of (rule set ID, rule set) if found, None otherwise.
        """
        # Check for repository-specific rule set
        rule_set_id = self._config.repository_rule_sets.get(repository.name)
        
        # Fall back to default rule set if no specific one is configured
        if not rule_set_id:
            rule_set_id = self._config.default_rule_set
        
        # Get the rule set from the rule manager
        rule_set = self._rule_manager.get_rule_set(rule_set_id)
        if rule_set:
            return (rule_set_id, rule_set)
        
        return None

    def lint_repositories(self, repositories: List[Repository]) -> Dict[str, Dict]:
        """Lint a list of repositories.
        
        Args:
            repositories: List of GitHub repositories to lint.
            
        Returns:
            Dictionary mapping repository names to their lint results.
            Each lint result is a dictionary mapping rule IDs to their check results.
        """
        results = {}
        
        for repo in repositories:
            # Create context for this repository
            context = self.create_context(repo)
            
            # Get rule set for this repository
            rule_set_info = self.get_rule_set_for_repository(repo)
            if not rule_set_info:
                print(f"Warning: No rule set found for repository {repo.name}")
                results[repo.name] = {
                    "error": f"No rule set found (tried: {self._config.repository_rule_sets.get(repo.name, self._config.default_rule_set)})"
                }
                continue
                
            rule_set_id, rule_set = rule_set_info
            print(f"Using rule set '{rule_set_id}' for repository {repo.name}")
            
            # TODO: Run rule set checks in next step
            results[repo.name] = {}
            
        return results
