from typing import Optional, TypeVar

_T = TypeVar("_T")


def cast_not_optional(optional: Optional[_T]) -> _T:
    """Convert an optional to its value for type checking purposes. Raises an AssertionError if passed None."""
    if optional is None:
        raise AssertionError("Not optional check failed")
    return optional
