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


def test_concat_expression_rhs_fail():
    # GIVEN a list lhs and a non-list rhs
    state = TestState()
    lhs_ref = ConstantValueReference([1, 2, 3])
    rhs_ref = ConstantValueReference(False)
    concat_expr = lhs_ref.concat(rhs_ref)

    # WHEN we attempt to resolve the expression
    with pytest.raises(InvalidExpressionException) as exc_info:
        concat_expr.resolve(state)

    # THEN an exception should be raised
    assert "Expected RHS to be a list, got <class 'bool'>" in str(exc_info.value)
