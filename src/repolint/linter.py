"""Core linting functionality for Repolint."""

from typing import Dict, List, Optional

from github.Repository import Repository

from repolint.config import BaseRepolintConfig
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

    def create_context(self, repository: Repository) -> RuleContext:
        """Create a rule context for a repository.
        
        Args:
            repository: GitHub repository to create context for.
            
        Returns:
            Rule context for the repository.
        """
        return RuleContext(repository=repository)

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
            # TODO: Get rule set for repository and run checks
            results[repo.name] = {}
            
        return results
