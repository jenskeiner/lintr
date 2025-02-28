"""Utility functions for the lintr package."""
import re
from typing import Final


def camel_to_hyphen(text: str) -> str:
    """Convert a camel case string to hyphen case.

    Args:
        text: The camel case string to convert

    Returns:
        The string converted to hyphen case

    Examples:
        >>> camel_to_hyphen("camelCase")
        'camel-case'
        >>> camel_to_hyphen("ThisIsATest")
        'this-is-a-test'
        >>> camel_to_hyphen("ABC")
        'abc'
        >>> camel_to_hyphen("already-hyphenated")
        'already-hyphenated'
    """
    pattern: Final = re.compile(r"(?<!^)(?=[A-Z])")
    return pattern.sub("-", text).lower()
