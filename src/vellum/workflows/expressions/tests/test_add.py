import pytest

from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.expressions.add import AddExpression
from vellum.workflows.state.base import BaseState


class TestState(BaseState):
    number_value: int = 5
    string_value: str = "hello"


def test_add_expression_numbers():
    """
    Tests that AddExpression correctly adds two numbers.
    """

    state = TestState()

    expression = TestState.number_value.add(10)

    result = expression.resolve(state)
    assert result == 15


def test_add_expression_strings():
    """
    Tests that AddExpression correctly concatenates two strings.
    """

    state = TestState()

    expression = TestState.string_value.add(" world")

    result = expression.resolve(state)
    assert result == "hello world"


def test_add_expression_unsupported_type():
    """
    Tests that AddExpression raises an exception for unsupported types.
    """

    class NoAddSupport:
        pass

    no_add_obj = NoAddSupport()
    expression = AddExpression(lhs=no_add_obj, rhs=5)
    state = TestState()

    with pytest.raises(InvalidExpressionException, match="'NoAddSupport' must support the '\\+' operator"):
        expression.resolve(state)


def test_add_expression_name():
    """
    Tests that AddExpression has the correct name.
    """

    expression = AddExpression(lhs=5, rhs=3)

    assert expression.name == "5 + 3"


def test_add_expression_types():
    """
    Tests that AddExpression has the correct types.
    """

    expression = AddExpression(lhs=5, rhs=3)

    assert expression.types == (object,)


def test_add_expression_list_plus_non_list():
    """
    Tests that AddExpression correctly handles list + non-list by wrapping non-list in a list.
    This allows State.chat_history + ChatMessage(...) to work.
    """

    state = TestState()

    # GIVEN a list and a non-list value
    my_list = [1, 2, 3]
    single_item = 4

    # WHEN we create an AddExpression and resolve it
    expression = AddExpression(lhs=my_list, rhs=single_item)
    result = expression.resolve(state)

    # THEN the result should be the list with the item appended
    assert result == [1, 2, 3, 4]
    assert isinstance(result, list)

    # AND the original list should be unchanged
    assert my_list == [1, 2, 3]
