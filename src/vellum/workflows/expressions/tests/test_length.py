import pytest

from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.expressions.length import LengthExpression
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.state.base import BaseState


class TestState(BaseState):
    pass


def test_length_expression_string():
    """
    Tests that LengthExpression correctly returns the length of a string.
    """

    state = TestState()

    string_value = "hello world"
    expression = LengthExpression(expression=string_value)

    result = expression.resolve(state)

    assert result == 11


def test_length_expression_list():
    """
    Tests that LengthExpression correctly returns the length of a list.
    """

    list_value = [1, 2, 3, 4, 5]
    expression = LengthExpression(expression=list_value)
    state = TestState()

    result = expression.resolve(state)

    assert result == 5


def test_length_expression_dict():
    """
    Tests that LengthExpression correctly returns the length of a dictionary.
    """

    dict_value = {"a": 1, "b": 2, "c": 3}
    expression = LengthExpression(expression=dict_value)
    state = TestState()

    result = expression.resolve(state)

    assert result == 3


def test_length_expression_tuple():
    """
    Tests that LengthExpression correctly returns the length of a tuple.
    """

    tuple_value = (1, 2, 3, 4)
    expression = LengthExpression(expression=tuple_value)
    state = TestState()

    result = expression.resolve(state)

    assert result == 4


def test_length_expression_set():
    """
    Tests that LengthExpression correctly returns the length of a set.
    """

    set_value = {1, 2, 3}
    expression = LengthExpression(expression=set_value)
    state = TestState()

    result = expression.resolve(state)

    assert result == 3


def test_length_expression_empty_collection():
    """
    Tests that LengthExpression correctly returns 0 for empty collections.
    """

    empty_list: list[int] = []
    expression = LengthExpression(expression=empty_list)
    state = TestState()

    result = expression.resolve(state)

    assert result == 0


def test_length_expression_undefined():
    """
    Tests that LengthExpression returns 0 for undefined values.
    """

    expression = LengthExpression(expression=undefined)
    state = TestState()

    result = expression.resolve(state)

    assert result == 0


def test_length_expression_unsupported_type():
    """
    Tests that LengthExpression raises an exception for unsupported types.
    """

    int_value = 42
    expression = LengthExpression(expression=int_value)
    state = TestState()

    with pytest.raises(InvalidExpressionException) as exc_info:
        expression.resolve(state)

    assert "Expected an object that supports `len()`" in str(exc_info.value)


def test_length_expression_with_descriptor():
    """
    Tests that LengthExpression works with BaseDescriptor references.
    """

    string_ref = ConstantValueReference("test string")
    expression: LengthExpression[str] = LengthExpression(expression=string_ref)
    state = TestState()

    result = expression.resolve(state)

    assert result == 11


def test_base_descriptor_length_method():
    """
    Tests that the length() method on BaseDescriptor works correctly.
    """

    string_ref = ConstantValueReference("hello")
    state = TestState()

    length_expr = string_ref.length()

    assert isinstance(length_expr, LengthExpression)

    result = length_expr.resolve(state)
    assert result == 5


def test_length_expression_name():
    """
    Tests that LengthExpression has the correct name format.
    """

    expression: LengthExpression[str] = LengthExpression(expression="test")

    assert expression.name == "length(test)"


def test_length_expression_types():
    """
    Tests that LengthExpression has the correct return type.
    """

    expression: LengthExpression[str] = LengthExpression(expression="test")

    assert expression.types == (int,)
