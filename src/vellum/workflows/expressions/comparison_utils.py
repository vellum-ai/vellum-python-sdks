from typing import Any


def try_parse_numeric_string(value: Any) -> Any:
    """
    Attempt to parse a string value as a number (int or float).

    This is to support the legacy workflow runner logic where string operands
    should be automatically parsed as numbers when compared with numeric types.

    Returns the parsed number if successful, otherwise returns the original value.
    """
    if not isinstance(value, str):
        return value

    try:
        if "." not in value:
            return int(value)
        return float(value)
    except (ValueError, TypeError):
        return value


def prepare_comparison_operands(lhs: Any, rhs: Any) -> tuple[Any, Any]:
    """
    Prepare operands for comparison by parsing string operands as numbers when appropriate.

    If one operand is a string and the other is a numeric type (int or float),
    attempts to parse the string as a number.

    Returns a tuple of (prepared_lhs, prepared_rhs).
    """
    if isinstance(lhs, str) and isinstance(rhs, (int, float)):
        lhs = try_parse_numeric_string(lhs)
    elif isinstance(rhs, str) and isinstance(lhs, (int, float)):
        rhs = try_parse_numeric_string(rhs)

    return lhs, rhs
