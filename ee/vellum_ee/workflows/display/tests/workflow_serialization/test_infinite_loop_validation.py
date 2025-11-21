import pytest

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.state.base import BaseState
from vellum_ee.workflows.display.utils.exceptions import NodeValidationError
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_workflow_serialization_error__node_points_to_itself():
    """
    Tests that serialization raises an error when a node creates an infinite loop by pointing to itself.

    This test documents the expected behavior for APO-2221: when a node in a workflow graph
    points back to itself (e.g., CheckPropertyExists >> CheckPropertyExists), the serialization
    should detect this infinite loop and raise a NodeValidationError.
    """

    class State(BaseState):
        property_exists: bool = False

    class CheckPropertyExists(BaseNode[State]):
        class Ports(BaseNode.Ports):
            property_exists = Port.on_if(State.property_exists.equals(True))
            create_property = Port.on_else()

        class Outputs(BaseNode.Outputs):
            exists: bool

    class StartNode(BaseNode[State]):
        pass

    class FinalOutput(BaseNode[State]):
        class Outputs(BaseNode.Outputs):
            result: str

    class InfiniteLoopWorkflow(BaseWorkflow[BaseInputs, State]):
        graph = (
            StartNode
            >> CheckPropertyExists
            >> {
                CheckPropertyExists.Ports.property_exists >> CheckPropertyExists,
                CheckPropertyExists.Ports.create_property >> FinalOutput,
            }
        )

        class Outputs(BaseWorkflow.Outputs):
            final = FinalOutput.Outputs.result

    workflow_display = get_workflow_display(workflow_class=InfiniteLoopWorkflow)

    with pytest.raises(NodeValidationError) as exc_info:
        workflow_display.serialize()

    error_message = str(exc_info.value)
    assert "infinite loop" in error_message.lower() or "circular" in error_message.lower()
    assert "CheckPropertyExists" in error_message
