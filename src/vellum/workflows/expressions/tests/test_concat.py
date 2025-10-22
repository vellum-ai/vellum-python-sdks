import pytest

from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.state.base import BaseState


class TestState(BaseState):
    pass


def test_concat_expression_happy_path():
    # GIVEN two lists
    state = TestState()
    lhs_ref = ConstantValueReference([1, 2, 3])
    rhs_ref = ConstantValueReference([4, 5, 6])
    concat_expr = lhs_ref.concat(rhs_ref)

    # WHEN we resolve the expression
    result = concat_expr.resolve(state)

    # THEN the lists should be concatenated
    assert result == [1, 2, 3, 4, 5, 6]


def test_concat_expression_lhs_fail():
    # GIVEN a non-list lhs and a list rhs
    state = TestState()
    lhs_ref = ConstantValueReference(0)
    rhs_ref = ConstantValueReference([4, 5, 6])
    concat_expr = lhs_ref.concat(rhs_ref)

    # WHEN we attempt to resolve the expression
    with pytest.raises(InvalidExpressionException) as exc_info:
        concat_expr.resolve(state)

    # THEN an exception should be raised
    assert "Expected LHS to be a list, got <class 'int'>" in str(exc_info.value)


def test_concat_expression_with_single_item():
    # GIVEN a list and a single item
    state = TestState()
    lhs_ref = ConstantValueReference([1, 2, 3])
    rhs_ref = ConstantValueReference(4)
    concat_expr = lhs_ref.concat(rhs_ref)

    # WHEN we resolve the expression
    result = concat_expr.resolve(state)

    # THEN the item should be appended to the list
    assert result == [1, 2, 3, 4]


def test_concat_expression_with_string():
    # GIVEN a list and a string item
    state = TestState()
    lhs_ref = ConstantValueReference(["hello", "world"])
    rhs_ref = ConstantValueReference("!")
    concat_expr = lhs_ref.concat(rhs_ref)

    # WHEN we resolve the expression
    result = concat_expr.resolve(state)

    # THEN the string should be appended to the list
    assert result == ["hello", "world", "!"]


def test_concat_expression_with_none():
    # GIVEN a list and None item
    state = TestState()
    lhs_ref = ConstantValueReference([1, 2])
    rhs_ref = ConstantValueReference(None)
    concat_expr = lhs_ref.concat(rhs_ref)

    # WHEN we resolve the expression
    result = concat_expr.resolve(state)

    # THEN None should be appended to the list
    assert result == [1, 2, None]


def test_concat_expression_with_list_item():
    # GIVEN a list and another list
    state = TestState()
    lhs_ref = ConstantValueReference([1, 2])
    rhs_ref = ConstantValueReference([3, 4])
    concat_expr = lhs_ref.concat(rhs_ref)

    # WHEN we resolve the expression
    result = concat_expr.resolve(state)

    # THEN the lists should be concatenated normally
    assert result == [1, 2, 3, 4]


def test_concat_expression_empty_list():
    # GIVEN an empty list and an item
    state = TestState()
    lhs_ref: ConstantValueReference[list] = ConstantValueReference([])
    rhs_ref = ConstantValueReference("first")
    concat_expr = lhs_ref.concat(rhs_ref)

    # WHEN we resolve the expression
    result = concat_expr.resolve(state)

    # THEN the item should be appended to the empty list
    assert result == ["first"]
