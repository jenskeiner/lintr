"""Context object for rule execution."""

from dataclasses import dataclass

from github.Repository import Repository


@dataclass
class RuleContext:
    """Context object passed to rules during execution.
    
    This class encapsulates all the information available to a rule when it runs.
    Currently, it contains:
    - repository: The GitHub repository object
    - dry_run: Whether to make actual changes or just simulate them
    """
    repository: Repository
    dry_run: bool = False
