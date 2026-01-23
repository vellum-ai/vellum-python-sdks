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
    assert mock.when_condition.resolve(None) == expected_value  # type: ignore[arg-type]


def test_mocks__when_condition_dict_with_type_and_valid_descriptor():
    """Tests that a dict with 'type' key uses descriptor_validator from context."""

    # GIVEN a Base Node
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND a descriptor_validator that returns a specific descriptor
    expected_descriptor = ConstantValueReference("validated")

    def mock_descriptor_validator(value):
        return expected_descriptor

    # WHEN we create a MockNodeExecution via model_validate with a dict containing 'type'
    mock = MockNodeExecution.model_validate(
        {
            "when_condition": {"type": "SOME_DESCRIPTOR", "value": "test"},
            "then_outputs": StartNode.Outputs(foo="mocked"),
        },
        context={"descriptor_validator": mock_descriptor_validator},
    )

    # THEN the when_condition should be the result from descriptor_validator
    assert mock.when_condition is expected_descriptor


def test_mocks__when_condition_dict_with_type_no_descriptor_validator():
    """Tests that a dict with 'type' key defaults to ConstantValueReference(False) without descriptor_validator."""

    # GIVEN a Base Node
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # WHEN we create a MockNodeExecution via model_validate with a dict containing 'type' but no descriptor_validator
    mock = MockNodeExecution.model_validate(
        {
            "when_condition": {"type": "SOME_DESCRIPTOR", "value": "test"},
            "then_outputs": StartNode.Outputs(foo="mocked"),
        },
    )

    # THEN the when_condition should default to ConstantValueReference(False)
    assert isinstance(mock.when_condition, ConstantValueReference)
    assert mock.when_condition.resolve(None) is False  # type: ignore[arg-type]


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
