"""
Single failing test for coalesce operator with undefined property access.

This test reproduces the issue from Linear ticket APO-1464 where expressions
like A ?? B.c result in unhelpful error messages when A is defined but B is undefined.
"""

from vellum.workflows.constants import undefined
from vellum.workflows.expressions.accessor import AccessorExpression
from vellum.workflows.expressions.coalesce_expression import CoalesceExpression
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.state.base import BaseState


def test_coalesce_with_undefined_property_access_error():
    """
    Test that reproduces the coalesce operator error when trying to access
    a property on an undefined value in expressions like A ?? B.c where
    A is defined but B is undefined.

    This test demonstrates the current unhelpful error message that needs improvement.
    """
    # GIVEN a coalesce expression A ?? B.c where A is undefined and B is undefined

    # Create B.c (property access on undefined/None value)
    undefined_value = ConstantValueReference(None)
    property_access = AccessorExpression(base=undefined_value, field="some_property")

    defined_value = ConstantValueReference(undefined)

    # Create the coalesce expression A ?? B.c
    coalesce_expr = CoalesceExpression(lhs=defined_value, rhs=property_access)

    state = BaseState()

    # THEN we should get the current unhelpful error message
    try:
        result = coalesce_expr.resolve(state)
        assert False, f"Expected expression to fail with unhelpful error, but got: {result}"
    except Exception as e:
        error_message = str(e)

        # This assertion will fail, demonstrating the current unhelpful error message
        assert "helpful error message about coalesce operator" in error_message, (
            f"Current unhelpful error message: {error_message}. "
            f"This should be improved to provide better context about the coalesce operator."
        )
