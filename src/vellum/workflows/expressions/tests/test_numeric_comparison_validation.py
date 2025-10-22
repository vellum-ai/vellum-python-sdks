"""
Tests for numeric comparison validation in comparison expressions.

This test file specifically tests that comparison operators (>, >=, <, <=)
properly validate that operands are numeric types and raise InvalidExpressionException
when non-numeric types (like strings) are used.
"""

import pytest

from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.expressions.between import BetweenExpression
from vellum.workflows.expressions.greater_than import GreaterThanExpression
from vellum.workflows.expressions.greater_than_or_equal_to import GreaterThanOrEqualToExpression
from vellum.workflows.expressions.less_than import LessThanExpression
from vellum.workflows.expressions.less_than_or_equal_to import LessThanOrEqualToExpression
from vellum.workflows.state.base import BaseState


class TestState(BaseState):
    pass


def test_greater_than_or_equal_to__string_comparison_error():
    """
    Test that reproduces the internal server error when doing string greater than or equal comparisons.
    This should raise a user-facing error instead of causing an internal server error.
    """
    # GIVEN string values
    state = TestState()

    # WHEN comparing strings with >=
    with pytest.raises(InvalidExpressionException) as exc_info:
        GreaterThanOrEqualToExpression(lhs="hello", rhs="world").resolve(state)

    # THEN the error message should be informative
    assert "Cannot perform '>=' comparison" in str(exc_info.value)
    assert "left operand must be numeric" in str(exc_info.value)
    assert "str" in str(exc_info.value)


def test_greater_than_or_equal_to__mixed_type_comparison_error():
    """Test that comparing a number with a string raises InvalidExpressionException"""
    # GIVEN a number and a string
    state = TestState()

    # WHEN comparing number with string
    with pytest.raises(InvalidExpressionException) as exc_info:
        GreaterThanOrEqualToExpression(lhs=10, rhs="world").resolve(state)

    # THEN the error message should be informative
    assert "Cannot perform '>=' comparison" in str(exc_info.value)
    assert "right operand must be numeric" in str(exc_info.value)
    assert "str" in str(exc_info.value)


def test_greater_than__string_comparison_error():
    """Test that string comparisons with > raise InvalidExpressionException"""
    # GIVEN string values
    state = TestState()

    # WHEN comparing strings with >
    with pytest.raises(InvalidExpressionException) as exc_info:
        GreaterThanExpression(lhs="hello", rhs="world").resolve(state)

    # THEN the error message should be informative
    assert "Cannot perform '>' comparison" in str(exc_info.value)
    assert "left operand must be numeric" in str(exc_info.value)


def test_less_than_or_equal_to__string_comparison_error():
    """Test that string comparisons with <= raise InvalidExpressionException"""
    # GIVEN string values
    state = TestState()

    # WHEN comparing strings with <=
    with pytest.raises(InvalidExpressionException) as exc_info:
        LessThanOrEqualToExpression(lhs="hello", rhs="world").resolve(state)

    # THEN the error message should be informative
    assert "Cannot perform '<=' comparison" in str(exc_info.value)
    assert "left operand must be numeric" in str(exc_info.value)


def test_less_than__string_comparison_error():
    """Test that string comparisons with < raise InvalidExpressionException"""
    # GIVEN string values
    state = TestState()

    # WHEN comparing strings with <
    with pytest.raises(InvalidExpressionException) as exc_info:
        LessThanExpression(lhs="hello", rhs="world").resolve(state)

    # THEN the error message should be informative
    assert "Cannot perform '<' comparison" in str(exc_info.value)
    assert "left operand must be numeric" in str(exc_info.value)


def test_between__string_comparison_error():
    """
    Test that reproduces the internal server error when doing BETWEEN comparisons with non-numeric strings.
    The BETWEEN operator should validate types and raise InvalidExpressionException.
    """
    # GIVEN string values
    state = TestState()

    # WHEN using between with strings
    with pytest.raises(InvalidExpressionException) as exc_info:
        BetweenExpression(value="hello", start="world", end="universe").resolve(state)

    # THEN the error message should be informative
    assert "Expected a numeric value" in str(exc_info.value)
    assert "str" in str(exc_info.value)
