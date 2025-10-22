"""
Test for APO-1936: Conditional nodes internal server error when doing string greater than or equal comparisons.

This test reproduces the error at the node level by creating a workflow node with ports that use
comparison expressions on string values.
"""

import pytest

from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.ports.port import Port
from vellum.workflows.state.base import BaseState, StateMeta


def test_conditional_node__string_greater_than_or_equal_comparison_error():
    """
    Test that reproduces the internal server error when doing string greater than or equal comparisons.
    This should raise a user-facing error instead of allowing string comparisons.

    Reproduces: https://linear.app/vellum/issue/APO-1936
    """

    # GIVEN workflow inputs with string values
    class Inputs(BaseInputs):
        field: str
        value: str

    class State(BaseState):
        pass

    # AND a conditional node that compares strings with >=
    class ConditionalNode(BaseNode[State]):
        class Ports(BaseNode.Ports):
            if_port = Port.on_if(Inputs.field.greater_than_or_equal_to(Inputs.value))
            else_port = Port.on_else()

        class Outputs(BaseOutputs):
            result: str

        def run(self) -> Outputs:
            return self.Outputs(result="executed")

    # WHEN we initialize the node with string inputs
    state = State(
        meta=StateMeta(
            workflow_inputs=Inputs(field="hello", value="world"),
        )
    )

    # THEN it should raise InvalidExpressionException when evaluating the port condition
    with pytest.raises(InvalidExpressionException) as exc_info:
        ConditionalNode(state=state)

    # AND the error message should be informative
    assert "numeric" in str(exc_info.value).lower() or "comparison" in str(exc_info.value).lower()
