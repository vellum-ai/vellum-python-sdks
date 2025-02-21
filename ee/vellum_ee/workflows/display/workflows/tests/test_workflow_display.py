import pytest

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.workflows import VellumWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_serialize_workflow__node_referenced_in_workflow_outputs_not_in_graph():
    # GIVEN a couple of nodes
    class InNode(BaseNode):
        pass

    class OutNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND A workflow that references the OutNode in its outputs but only has the InNode in its graph
    class Workflow(BaseWorkflow):
        graph = InNode

        class Outputs(BaseWorkflow.Outputs):
            final = OutNode.Outputs.foo

    # WHEN we serialize it
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay,
        workflow_class=Workflow,
    )

    # THEN it should raise an error
    with pytest.raises(ValueError) as exc_info:
        workflow_display.serialize()

    # AND the error message should be user friendly
    assert str(exc_info.value) == "Failed to serialize output 'final': Reference to node 'OutNode' not found in graph."


def test_serialize_workflow__workflow_outputs_reference_non_node_outputs():
    # GIVEN one Workflow
    class FirstWorkflow(BaseWorkflow):
        class Outputs(BaseWorkflow.Outputs):
            foo = "bar"

    # AND A workflow that references the Outputs of that Workflow
    class Workflow(BaseWorkflow):
        class Outputs(BaseWorkflow.Outputs):
            final = FirstWorkflow.Outputs.foo

    # WHEN we serialize it
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay,
        workflow_class=Workflow,
    )

    # THEN it should raise an error
    with pytest.raises(ValueError) as exc_info:
        workflow_display.serialize()

    # AND the error message should be user friendly
    assert (
        str(exc_info.value)
        == """Failed to serialize output 'final': Reference to outputs \
'test_serialize_workflow__workflow_outputs_reference_non_node_outputs.<locals>.FirstWorkflow.Outputs' is invalid."""
    )


def test_serialize_workflow__node_display_class_not_registered():
    # GIVEN a workflow with a node that has a display class referencing display data
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    class StartNodeDisplay(BaseNodeDisplay[StartNode]):
        node_input_ids_by_name = {}
        display_data = NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=None, height=None)

    class MyWorkflow(BaseWorkflow):
        graph = StartNode

        class Outputs(BaseWorkflow.Outputs):
            answer = StartNode.Outputs.result

    # WHEN we serialize it
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay,
        workflow_class=MyWorkflow,
    )
    data = workflow_display.serialize()

    # THEN it should should succeed
    assert data is not None
