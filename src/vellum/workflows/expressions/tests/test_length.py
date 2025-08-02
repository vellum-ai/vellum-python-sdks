import pytest

from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.expressions.length import LengthExpression
from vellum.workflows.state.base import BaseState


class TestState(BaseState):
    string_value: str = "hello world"


def test_length_expression_string():
    """
    Tests that LengthExpression correctly returns the length of a string.
    """

    state = TestState()

    expression = TestState.string_value.length()
    result = expression.resolve(state)

    assert result == 11


def test_length_expression_undefined():
    """
    Tests that LengthExpression raises an exception for undefined values.
    """

    expression = LengthExpression(expression=undefined)
    state = TestState()

    # THEN we should get an InvalidExpressionException
    with pytest.raises(InvalidExpressionException) as exc_info:
        expression.resolve(state)

    assert "Cannot get length of undefined value" in str(exc_info.value)
