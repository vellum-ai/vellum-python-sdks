import pytest

from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.expressions.minus import MinusExpression
from vellum.workflows.state.base import BaseState


class TestState(BaseState):
    number_value: int = 10
    float_value: float = 15.5


def test_minus_expression_numbers():
    """
    Tests that MinusExpression correctly subtracts two numbers.
    """

    state = TestState()

    expression = TestState.number_value.minus(3)

    result = expression.resolve(state)
    assert result == 7


def test_minus_expression_floats():
    """
    Tests that MinusExpression correctly subtracts two floats.
    """

    state = TestState()

    expression = TestState.float_value.minus(5.5)

    result = expression.resolve(state)
    assert result == 10.0


def test_minus_expression_unsupported_type():
    """
    Tests that MinusExpression raises an exception for unsupported types.
    """

    class NoSubSupport:
        pass

    no_sub_obj = NoSubSupport()
    expression = MinusExpression(lhs=no_sub_obj, rhs=5)
    state = TestState()

    with pytest.raises(InvalidExpressionException, match="'NoSubSupport' must support the '-' operator"):
        expression.resolve(state)


def test_minus_expression_name():
    """
    Tests that MinusExpression has the correct name.
    """

    expression = MinusExpression(lhs=10, rhs=3)

    assert expression.name == "10 - 3"


def test_minus_expression_types():
    """
    Tests that MinusExpression has the correct types.
    """

    expression = MinusExpression(lhs=10, rhs=3)

    assert expression.types == (object,)
