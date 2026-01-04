from vellum.workflows import BaseWorkflow
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.references.constant import ConstantValueReference

from tests.workflows.invalid_port_resolution.workflow import InvalidPortResolutionWorkflow


def test_workflow__expected_path():
    """
    Confirm that we raise the correct error when the port resolution is invalid.
    """

    # GIVEN a workflow with an invalid port description
    workflow = InvalidPortResolutionWorkflow()

    # WHEN the workflow is executed
    final_event = workflow.run()

    # THEN the workflow raises the correct error
    assert final_event.name == "workflow.execution.rejected"
    assert final_event.error.code == WorkflowErrorCode.INVALID_INPUTS
    assert (
        final_event.error.message
        == "Failed to resolve condition for port `foo`: Expected a LHS that supported `contains`, got `int`"
    )


def test_workflow__raw_data_includes_outputs():
    """
    Confirm that port resolution errors include the node's outputs in raw_data.
    """

    # GIVEN a node with outputs and an invalid port condition
    class NodeWithOutputs(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

        class Ports(BaseNode.Ports):
            foo = Port.on_if(ConstantValueReference(1).contains("bar"))

        def run(self) -> Outputs:
            return self.Outputs(result="test_value")

    class OtherNode(BaseNode):
        pass

    class WorkflowWithOutputs(BaseWorkflow):
        graph = NodeWithOutputs.Ports.foo >> OtherNode

        class Outputs(BaseWorkflow.Outputs):
            pass

    workflow = WorkflowWithOutputs()

    # WHEN the workflow is executed
    final_event = workflow.run()

    # THEN the error includes the node's outputs in raw_data
    assert final_event.name == "workflow.execution.rejected"
    assert final_event.error.code == WorkflowErrorCode.INVALID_INPUTS
    assert final_event.error.raw_data == {"outputs": {"result": "test_value"}}
