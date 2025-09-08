import pytest

from vellum.workflows.constants import undefined
from vellum.workflows.expressions.accessor import AccessorExpression
from vellum.workflows.expressions.coalesce_expression import CoalesceExpression
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.state.base import BaseState


class TestState(BaseState):
    pass


def test_coalesce_with_undefined_property_access_error():
    """
    Test that reproduces the coalesce operator error when trying to access
    a property on an undefined value in expressions like A ?? B.c where
    A is defined but B is undefined.

    This test should fail with the current unhelpful error message.
    """
    # GIVEN a coalesce expression A ?? B.c where A is defined but B is undefined
    # This represents: "defined_value" ?? undefined_value.some_property

    undefined_value = ConstantValueReference(undefined)

    # Create B.c (property access on undefined)
    property_access_expression = AccessorExpression(
        base=undefined_value,
        field="some_property",
    )

    # Create the coalesce expression A ?? B.c
    defined_value = ConstantValueReference("defined_value")
    coalesce_expression = CoalesceExpression(
        lhs=defined_value,
        rhs=property_access_expression,
    )

    state = TestState()

    result = coalesce_expression.resolve(state)

    # and never evaluate the RHS (property access on undefined)
    assert result == "defined_value"


def test_coalesce_basic_functionality():
    """
    Test that basic coalesce functionality still works correctly.
    """
    lhs = ConstantValueReference("first_value")
    rhs = ConstantValueReference("second_value")
    coalesce_expression = CoalesceExpression(lhs=lhs, rhs=rhs)

    state = TestState()

    result = coalesce_expression.resolve(state)

    assert result == "first_value"


def test_coalesce_with_undefined_lhs():
    """
    Test that coalesce works when LHS is undefined.
    """
    lhs = ConstantValueReference(undefined)
    rhs = ConstantValueReference("fallback_value")
    coalesce_expression = CoalesceExpression(lhs=lhs, rhs=rhs)

    state = TestState()

    result = coalesce_expression.resolve(state)

    assert result == "fallback_value"


def test_coalesce_with_undefined_property_access_error_both_undefined():
    """
    Test the scenario where both LHS is undefined/null and RHS tries to access
    a property on undefined. This should trigger the error.
    """
    # GIVEN a coalesce expression where LHS is undefined and RHS is B.c with B undefined
    # This represents: undefined ?? undefined_value.some_property

    # Create the undefined value B
    undefined_value = ConstantValueReference(undefined)

    # Create B.c (property access on undefined)
    property_access_expression = AccessorExpression(
        base=undefined_value,
        field="some_property",
    )

    # Create the coalesce expression undefined ?? B.c
    lhs_undefined = ConstantValueReference(undefined)
    coalesce_expression = CoalesceExpression(
        lhs=lhs_undefined,
        rhs=property_access_expression,
    )

    state = TestState()

    # This should fail when trying to access property on undefined
    with pytest.raises(Exception) as exc_info:
        coalesce_expression.resolve(state)

    # THEN we should get a helpful error message (this is what we want to improve)
    error_message = str(exc_info.value)

    # This assertion captures the current unhelpful error message
    assert (
        "Cannot get field some_property from" in error_message
    ), f"Expected current unhelpful error message, but got: {error_message}"
