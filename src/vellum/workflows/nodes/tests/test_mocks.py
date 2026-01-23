import pytest

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.mocks import MockNodeExecution
from vellum.workflows.references.constant import ConstantValueReference


@pytest.mark.parametrize(
    "when_condition,expected_value",
    [
        (True, True),
        (False, False),
        ("always", "always"),
        (42, 42),
        ({"key": "value"}, {"key": "value"}),
        ({"type": "SOME_DESCRIPTOR", "value": "test"}, {"type": "SOME_DESCRIPTOR", "value": "test"}),
    ],
)
def test_mocks__when_condition_constant(when_condition, expected_value):
    """Tests that MockNodeExecution accepts constant when_condition values and normalizes them."""

    # GIVEN a Base Node
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # WHEN we create a MockNodeExecution with a constant when_condition
    mock = MockNodeExecution(
        when_condition=when_condition,
        then_outputs=StartNode.Outputs(foo="mocked"),
    )

    # THEN the when_condition should be normalized to ConstantValueReference
    assert isinstance(mock.when_condition, ConstantValueReference)
    assert mock.when_condition._value == expected_value


def test_mocks__parse_none_still_runs():
    # GIVEN a Base Node
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND a workflow class with that Node
    class MyWorkflow(BaseWorkflow):
        graph = StartNode

        class Outputs(BaseWorkflow.Outputs):
            final_value = StartNode.Outputs.foo

    # AND we parsed `None` on `MockNodeExecution`
    node_output_mocks = MockNodeExecution.validate_all(
        None,
        MyWorkflow,
    )

    # WHEN we run the workflow
    workflow = MyWorkflow()
    final_event = workflow.run(node_output_mocks=node_output_mocks)

    # THEN it was successful
    assert final_event.name == "workflow.execution.fulfilled"
