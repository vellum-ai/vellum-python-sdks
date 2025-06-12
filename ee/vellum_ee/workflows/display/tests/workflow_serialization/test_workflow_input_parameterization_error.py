import pytest

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum_ee.workflows.display.utils.exceptions import UnsupportedSerializationException
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_workflow_serialization_error_when_node_references_unparameterized_inputs():
    """Test that a helpful error is raised when a node references inputs not parameterized by the workflow."""

    class CustomInputs(BaseInputs):
        custom_input: str

    class TestNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            output = CustomInputs.custom_input

    class TestWorkflow(BaseWorkflow):
        graph = TestNode

        class Outputs(BaseWorkflow.Outputs):
            result = TestNode.Outputs.output

    workflow_display = get_workflow_display(workflow_class=TestWorkflow)

    with pytest.raises(UnsupportedSerializationException) as exc_info:
        workflow_display.serialize()

    error_message = str(exc_info.value)
    assert "CustomInputs.custom_input" in error_message
    assert "parameterize" in error_message.lower()
    assert "inputs class that defines this input" in error_message
    assert "BaseWorkflow[" in error_message
    assert "YourState]" in error_message
