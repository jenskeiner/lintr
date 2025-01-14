"""Context object for rule execution."""

from dataclasses import dataclass

from github.Repository import Repository


@dataclass
class RuleContext:
    """Context object passed to rules during execution.
    
    This class encapsulates all the information available to a rule when it runs.
    Currently, it only contains the GitHub repository object, but can be expanded
    in the future to provide more context.
    """
    repository: Repository
