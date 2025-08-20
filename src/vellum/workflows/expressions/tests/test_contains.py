import pytest

from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.expressions.contains import ContainsExpression
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.state.base import BaseState


class TestState(BaseState):
    dict_value: dict = {"key": "value"}
    list_value: list = [1, 2, 3]
    string_value: str = "hello world"


def test_dict_contains_dict_raises_error():
    """
    Tests that ContainsExpression raises clear error for dict-contains-dict scenarios.
    """
    state = TestState()
    lhs_dict = {"foo": "bar"}
    rhs_dict = {"foo": "bar"}

    expression = ContainsExpression(lhs=lhs_dict, rhs=rhs_dict)

    with pytest.raises(InvalidExpressionException, match="Cannot use dict as right-hand side"):
        expression.resolve(state)


def test_dict_contains_different_dict_raises_error():
    """
    Tests that ContainsExpression raises clear error for different dict-contains-dict scenarios.
    """
    state = TestState()
    lhs_dict = {"foo": "bar"}
    rhs_dict = {"hello": "world"}

    expression = ContainsExpression(lhs=lhs_dict, rhs=rhs_dict)

    with pytest.raises(InvalidExpressionException, match="Cannot use dict as right-hand side"):
        expression.resolve(state)


def test_string_contains_dict_raises_error():
    """
    Tests that ContainsExpression raises clear error for string-contains-dict scenarios.
    """
    state = TestState()
    lhs_string = 'Response: {"status": "success"} was returned'
    rhs_dict = {"status": "success"}

    expression = ContainsExpression(lhs=lhs_string, rhs=rhs_dict)

    with pytest.raises(InvalidExpressionException, match="Cannot use dict as right-hand side"):
        expression.resolve(state)


def test_nested_dict_contains_dict_raises_error():
    """
    Tests that ContainsExpression raises clear error for nested dict scenarios.
    """
    state = TestState()
    lhs_dict = {"user": {"name": "john", "age": 30}}
    rhs_dict = {"age": 30, "name": "john"}

    expression = ContainsExpression(lhs=lhs_dict, rhs=rhs_dict)

    with pytest.raises(InvalidExpressionException, match="Cannot use dict as right-hand side"):
        expression.resolve(state)


def test_list_contains_string():
    """
    Tests that ContainsExpression preserves original list functionality.
    """
    state = TestState()

    expression = TestState.list_value.contains(2)
    result = expression.resolve(state)

    assert result is True


def test_string_contains_substring():
    """
    Tests that ContainsExpression preserves original string functionality.
    """
    state = TestState()

    expression = TestState.string_value.contains("world")
    result = expression.resolve(state)

    assert result is True


def test_set_contains_item():
    """
    Tests that ContainsExpression works with sets.
    """
    state = TestState()
    lhs_set = {1, 2, 3}
    rhs_item = 2

    expression = ContainsExpression(lhs=lhs_set, rhs=rhs_item)
    result = expression.resolve(state)

    assert result is True


def test_tuple_contains_item():
    """
    Tests that ContainsExpression works with tuples.
    """
    state = TestState()
    lhs_tuple = (1, 2, 3)
    rhs_item = 2

    expression = ContainsExpression(lhs=lhs_tuple, rhs=rhs_item)
    result = expression.resolve(state)

    assert result is True


def test_invalid_lhs_type():
    """
    Tests that ContainsExpression raises exception for invalid LHS types.
    """

    class NoContainsSupport:
        pass

    state = TestState()
    no_contains_obj = NoContainsSupport()
    expression = ContainsExpression(lhs=no_contains_obj, rhs="test")

    with pytest.raises(
        InvalidExpressionException, match="Expected a LHS that supported `contains`, got `NoContainsSupport`"
    ):
        expression.resolve(state)


def test_undefined_lhs_returns_false():
    """
    Tests that ContainsExpression returns False for undefined LHS.
    """
    state = TestState()
    expression = ContainsExpression(lhs=undefined, rhs="test")

    result = expression.resolve(state)

    assert result is False


def test_contains_with_constant_value_reference():
    """
    Tests ContainsExpression with ConstantValueReference for valid operations.
    """
    state = TestState()
    lhs_ref = ConstantValueReference([1, 2, 3])
    rhs_ref = ConstantValueReference(2)

    expression: ContainsExpression = ContainsExpression(lhs=lhs_ref, rhs=rhs_ref)
    result = expression.resolve(state)

    assert result is True


def test_expression_metadata():
    """
    Tests that ContainsExpression has correct name and types properties.
    """
    expression = ContainsExpression(lhs=[1, 2, 3], rhs=2)

    assert expression.name == "[1, 2, 3] contains 2"
    assert expression.types == (bool,)
