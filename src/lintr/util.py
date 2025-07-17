"""Utility functions for the lintr package."""
import re
from typing import Final, get_origin, get_args, Annotated, Union


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


def is_pydantic_tagged_union(type_hint) -> bool:
    """Check if a type is Annotated[Union[...], Field(discriminator="...")]"""

    # Check if it's an Annotated type
    if get_origin(type_hint) is not Annotated:
        return False

    args = get_args(type_hint)
    if len(args) < 2:
        return False

    # First argument should be a Union
    union_type = args[0]
    if get_origin(union_type) is not Union:
        return False

    # Check if any of the remaining arguments is a Field with discriminator
    for annotation in args[1:]:
        if (
            hasattr(annotation, "discriminator")
            and annotation.discriminator is not None
        ):
            return True

    return False


def is_compatible_with_expected_type(t, expected_type) -> bool:
    if t is expected_type:
        return True
    elif is_pydantic_tagged_union(expected_type):
        args = get_args(expected_type)
        union_type = args[0]
        union_args = get_args(union_type)

        # Check if any type in the union is compatible
        return any(is_compatible_with_expected_type(t, arg) for arg in union_args)
    elif is_pydantic_tagged_union(t):
        args = get_args(t)
        union_type = args[0]
        union_args = get_args(union_type)

        # Check each type in the union
        return all(
            is_compatible_with_expected_type(arg, expected_type) for arg in union_args
        )
    elif (
        isinstance(t, type)
        and isinstance(expected_type, type)
        and issubclass(t, expected_type)
    ):
        return True

    return False
