import pytest

from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.expressions.greater_than import GreaterThanExpression
from vellum.workflows.expressions.greater_than_or_equal_to import GreaterThanOrEqualToExpression
from vellum.workflows.expressions.less_than import LessThanExpression
from vellum.workflows.expressions.less_than_or_equal_to import LessThanOrEqualToExpression
from vellum.workflows.state.base import BaseState


class Comparable:
    """A custom class with two values, where comparisons use a computed metric (multiplication)."""

    def __init__(self, value1, value2):
        self.value1 = value1  # First numerical value
        self.value2 = value2  # Second numerical value

    def computed_value(self):
        return self.value1 * self.value2  # Multiply for comparison

    def __ge__(self, other):
        if isinstance(other, Comparable):
            return self.computed_value() >= other.computed_value()
        elif isinstance(other, (int, float)):
            return self.computed_value() >= other
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Comparable):
            return self.computed_value() > other.computed_value()
        elif isinstance(other, (int, float)):
            return self.computed_value() > other
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Comparable):
            return self.computed_value() <= other.computed_value()
        elif isinstance(other, (int, float)):
            return self.computed_value() <= other
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Comparable):
            return self.computed_value() < other.computed_value()
        elif isinstance(other, (int, float)):
            return self.computed_value() < other
        return NotImplemented


class NonComparable:
    """A custom class that does not support comparisons."""

    def __init__(self, value1, value2):
        self.value1 = value1
        self.value2 = value2


class TestState(BaseState):
    pass


def test_greater_than_or_equal_to():
    state = TestState()

    # WHEN comparing numbers
    assert GreaterThanOrEqualToExpression(lhs=20, rhs=20).resolve(state) is True  # 20 >= 20
    assert GreaterThanOrEqualToExpression(lhs=20, rhs=18).resolve(state) is True  # 20 >= 18
    assert GreaterThanOrEqualToExpression(lhs=18, rhs=25).resolve(state) is False  # 18 < 25
    assert GreaterThanOrEqualToExpression(lhs=20, rhs=19).resolve(state) is True  # 20 >= 19
    assert GreaterThanOrEqualToExpression(lhs=18, rhs=20).resolve(state) is False  # 18 < 20

    # WHEN comparing floats
    assert GreaterThanOrEqualToExpression(lhs=20.5, rhs=20.5).resolve(state) is True
    assert GreaterThanOrEqualToExpression(lhs=20.5, rhs=20.0).resolve(state) is True
    assert GreaterThanOrEqualToExpression(lhs=20.0, rhs=20.5).resolve(state) is False


def test_greater_than_or_equal_to_invalid():
    """Test that string comparisons raise InvalidExpressionException"""
    state = TestState()

    # WHEN comparing strings with >=
    with pytest.raises(InvalidExpressionException) as exc_info:
        GreaterThanOrEqualToExpression(lhs="hello", rhs="world").resolve(state)

    # THEN the expected error is raised
    assert "Cannot perform '>=' comparison" in str(exc_info.value)
    assert "left operand must be numeric" in str(exc_info.value)
    assert "str" in str(exc_info.value)

    # WHEN comparing number with string
    with pytest.raises(InvalidExpressionException) as exc_info:
        GreaterThanOrEqualToExpression(lhs=10, rhs="world").resolve(state)

    # THEN the expected error is raised
    assert "Cannot perform '>=' comparison" in str(exc_info.value)
    assert "right operand must be numeric" in str(exc_info.value)


def test_greater_than():
    state = TestState()

    # WHEN comparing numbers
    assert GreaterThanExpression(lhs=20, rhs=20).resolve(state) is False
    assert GreaterThanExpression(lhs=20, rhs=18).resolve(state) is True
    assert GreaterThanExpression(lhs=18, rhs=25).resolve(state) is False
    assert GreaterThanExpression(lhs=20, rhs=19).resolve(state) is True
    assert GreaterThanExpression(lhs=18, rhs=20).resolve(state) is False

    # WHEN comparing floats
    assert GreaterThanExpression(lhs=20.5, rhs=20.0).resolve(state) is True
    assert GreaterThanExpression(lhs=20.0, rhs=20.5).resolve(state) is False


def test_greater_than_invalid():
    """Test that string comparisons raise InvalidExpressionException"""
    state = TestState()

    # WHEN comparing strings with >
    with pytest.raises(InvalidExpressionException) as exc_info:
        GreaterThanExpression(lhs="hello", rhs="world").resolve(state)

    # THEN the expected error is raised
    assert "Cannot perform '>' comparison" in str(exc_info.value)
    assert "left operand must be numeric" in str(exc_info.value)


def test_less_than_or_equal_to():
    state = TestState()

    # WHEN comparing numbers
    assert LessThanOrEqualToExpression(lhs=20, rhs=20).resolve(state) is True
    assert LessThanOrEqualToExpression(lhs=20, rhs=18).resolve(state) is False
    assert LessThanOrEqualToExpression(lhs=18, rhs=25).resolve(state) is True
    assert LessThanOrEqualToExpression(lhs=20, rhs=21).resolve(state) is True
    assert LessThanOrEqualToExpression(lhs=18, rhs=17).resolve(state) is False

    # WHEN comparing floats
    assert LessThanOrEqualToExpression(lhs=20.0, rhs=20.5).resolve(state) is True
    assert LessThanOrEqualToExpression(lhs=20.5, rhs=20.0).resolve(state) is False


def test_less_than_or_equal_to_invalid():
    """Test that string comparisons raise InvalidExpressionException"""
    state = TestState()

    # WHEN comparing strings with <=
    with pytest.raises(InvalidExpressionException) as exc_info:
        LessThanOrEqualToExpression(lhs="hello", rhs="world").resolve(state)

    # THEN the expected error is raised
    assert "Cannot perform '<=' comparison" in str(exc_info.value)
    assert "left operand must be numeric" in str(exc_info.value)


def test_less_than():
    state = TestState()

    # WHEN comparing numbers
    assert LessThanExpression(lhs=20, rhs=20).resolve(state) is False
    assert LessThanExpression(lhs=20, rhs=18).resolve(state) is False
    assert LessThanExpression(lhs=18, rhs=25).resolve(state) is True
    assert LessThanExpression(lhs=20, rhs=21).resolve(state) is True
    assert LessThanExpression(lhs=18, rhs=17).resolve(state) is False

    # WHEN comparing floats
    assert LessThanExpression(lhs=20.0, rhs=20.5).resolve(state) is True
    assert LessThanExpression(lhs=20.5, rhs=20.0).resolve(state) is False


def test_less_than_invalid():
    """Test that string comparisons raise InvalidExpressionException"""
    state = TestState()

    # WHEN comparing strings with <
    with pytest.raises(InvalidExpressionException) as exc_info:
        LessThanExpression(lhs="hello", rhs="world").resolve(state)

    # THEN the expected error is raised
    assert "Cannot perform '<' comparison" in str(exc_info.value)
    assert "left operand must be numeric" in str(exc_info.value)
