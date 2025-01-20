"""Core linting functionality."""

from typing import Dict, List, Optional, Tuple

from github.Repository import Repository

from repolint.config import BaseRepolintConfig
from repolint.rule_manager import RuleManager
from repolint.rules import RuleCheckResult, RuleSet
from repolint.rules.context import RuleContext
from repolint.rules import RuleResult


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
        
        # Load rule sets from configuration
        self._rule_manager.load_rule_sets_from_config(config)

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

    def check_repository(self, repository: Repository, rule_set: RuleSet) -> Dict[str, RuleCheckResult]:
        """Check a repository against all rules in a rule set.
        
        Args:
            repository: GitHub repository to check.
            rule_set: Rule set to use for checking.
            
        Returns:
            Dictionary mapping rule IDs to their check results.
        """
        context = self.create_context(repository)
        results = {}
        
        # Execute each rule from the rule set
        for rule in rule_set.rules():
            try:
                results[rule.rule_id] = rule.check(context)
            except Exception as e:
                print(f"Error executing rule {rule.rule_id} on repository {repository.name}: {e}")
                results[rule.rule_id] = RuleCheckResult(
                    result=RuleResult.FAILED,
                    message=f"Rule execution failed: {str(e)}",
                    fix_available=False
                )
                
        return results

    def lint_repositories(self, repositories: List[Repository]) -> Dict[str, Dict[str, RuleCheckResult]]:
        """Lint a list of repositories.
        
        Args:
            repositories: List of GitHub repositories to lint.
            
        Returns:
            Dictionary mapping repository names to their lint results.
            Each lint result is a dictionary mapping rule IDs to their check results.
        """
        results = {}
        
        for repo in repositories:
            # Get rule set for this repository
            rule_set_info = self.get_rule_set_for_repository(repo)
            if not rule_set_info:
                print(f"- {repo.name} (no rule set)")
                results[repo.name] = {
                    "error": f"No rule set found (tried: {self._config.repository_rule_sets.get(repo.name, self._config.default_rule_set)})"
                }
                continue
                
            rule_set_id, rule_set = rule_set_info
            print(f"- {repo.name} ({rule_set_id})")
            
            # Run all rules in the rule set
            try:
                rule_results = self.check_repository(repo, rule_set)
                results[repo.name] = rule_results
                
                # Print rule results
                for rule_id, result in rule_results.items():
                    status_symbol = "✓" if result.result == RuleResult.PASSED else "✗" if result.result == RuleResult.FAILED else "-"
                    print(f"  {status_symbol} {rule_id}: {result.message}")
                    if result.fix_available:
                        print(f"    ⚡ {result.fix_description}")
                
            except Exception as e:
                print(f"  Error: {str(e)}")
                results[repo.name] = {
                    "error": f"Failed to check repository: {str(e)}"
                }
            
        return results
