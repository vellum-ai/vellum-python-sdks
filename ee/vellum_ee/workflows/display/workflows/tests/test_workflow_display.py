import pytest
from uuid import uuid4

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.inline_subworkflow_node.node import InlineSubworkflowNode
from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum.workflows.nodes.core.templating_node.node import TemplatingNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.editor.types import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.vellum.retry_node import BaseRetryNodeDisplay
from vellum_ee.workflows.display.nodes.vellum.try_node import BaseTryNodeDisplay
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


def test_get_event_display_context__node_display_filled_without_base_display():
    # GIVEN a simple workflow
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    # WHEN we gather the event display context
    display_context = VellumWorkflowDisplay(MyWorkflow).get_event_display_context()

    # THEN the node display should be included
    assert StartNode.__id__ in display_context.node_displays
    node_event_display = display_context.node_displays[StartNode.__id__]

    # AND so should their output ids
    assert StartNode.__output_ids__ == node_event_display.output_display


def test_get_event_display_context__node_display_filled_without_output_display():
    # GIVEN a simple workflow
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    class StartNodeDisplay(BaseNodeDisplay[StartNode]):
        pass

    # WHEN we gather the event display context
    display_context = VellumWorkflowDisplay(MyWorkflow).get_event_display_context()

    # THEN the node display should be included
    assert StartNode.__id__ in display_context.node_displays
    node_event_display = display_context.node_displays[StartNode.__id__]

    # AND so should their output ids
    assert node_event_display.output_display.keys() == {"foo"}


def test_get_event_display_context__node_display_to_include_subworkflow_display():
    # GIVEN a simple workflow
    class InnerNode(BaseNode):
        pass

    class Subworkflow(BaseWorkflow):
        graph = InnerNode

    # AND a workflow that includes the subworkflow
    class SubworkflowNode(InlineSubworkflowNode):
        subworkflow = Subworkflow

    class MyWorkflow(BaseWorkflow):
        graph = SubworkflowNode

    # WHEN we gather the event display context
    display_context = VellumWorkflowDisplay(MyWorkflow).get_event_display_context()

    # THEN the subworkflow display should be included
    assert SubworkflowNode.__id__ in display_context.node_displays
    node_event_display = display_context.node_displays[SubworkflowNode.__id__]

    assert node_event_display.subworkflow_display is not None
    assert InnerNode.__id__ in node_event_display.subworkflow_display.node_displays


@pytest.mark.parametrize(
    ["AdornmentNode", "AdornmentNodeDisplay", "expected_adornment_output_names"],
    [
        [RetryNode, BaseRetryNodeDisplay, {"foo"}],
        [TryNode, BaseTryNodeDisplay, {"foo", "error"}],
    ],
    ids=["retry_node", "try_node"],
)
def test_get_event_display_context__node_display_for_adornment_nodes(
    AdornmentNode,
    AdornmentNodeDisplay,
    expected_adornment_output_names,
):
    # GIVEN a simple workflow with an adornment
    @AdornmentNode.wrap()
    class MyNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = MyNode

    # AND a display class for the node
    adornment_node_id = uuid4()
    inner_node_id = uuid4()

    @AdornmentNodeDisplay.wrap(node_id=adornment_node_id)
    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        node_id = inner_node_id

    # WHEN we gather the event display context
    display_context = VellumWorkflowDisplay(MyWorkflow).get_event_display_context()

    # THEN the subworkflow display should be included
    assert adornment_node_id in display_context.node_displays
    node_event_display = display_context.node_displays[adornment_node_id]
    assert node_event_display.subworkflow_display is not None
    assert inner_node_id in node_event_display.subworkflow_display.node_displays

    # AND the inner node should have the correct outputs
    inner_node_display = node_event_display.subworkflow_display.node_displays[inner_node_id]
    assert inner_node_display.output_display.keys() == {"foo"}
    assert node_event_display.output_display.keys() == expected_adornment_output_names


def test_get_event_display_context__templating_node_input_display():
    # GIVEN a simple workflow with a templating node referencing another node output
    class DataNode(BaseNode):
        class Outputs:
            bar: str

    class MyNode(TemplatingNode):
        inputs = {"foo": DataNode.Outputs.bar}

    class MyWorkflow(BaseWorkflow):
        graph = DataNode >> MyNode

    # WHEN we gather the event display context
    display_context = VellumWorkflowDisplay(MyWorkflow).get_event_display_context()

    # THEN the subworkflow display should be included
    assert MyNode.__id__ in display_context.node_displays
    node_event_display = display_context.node_displays[MyNode.__id__]

    assert node_event_display.input_display.keys() == {"inputs.foo"}


def test_get_event_display_context__node_display_for_mutiple_adornments():
    # GIVEN a simple workflow with multiple adornments
    @TryNode.wrap()
    @RetryNode.wrap()
    class MyNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = MyNode

    # AND a display class for the node
    node_id = uuid4()
    inner_node_id = uuid4()
    innermost_node_id = uuid4()

    @BaseTryNodeDisplay.wrap(node_id=node_id)
    @BaseRetryNodeDisplay.wrap(node_id=inner_node_id)
    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        node_id = innermost_node_id

    # WHEN we gather the event display context
    display_context = VellumWorkflowDisplay(MyWorkflow).get_event_display_context()

    # THEN the subworkflow display should be included
    assert node_id in display_context.node_displays
    node_event_display = display_context.node_displays[node_id]
    assert node_event_display.subworkflow_display

    # AND the inner node should be included
    assert inner_node_id in node_event_display.subworkflow_display.node_displays
    inner_node_event_display = node_event_display.subworkflow_display.node_displays[inner_node_id]
    assert inner_node_event_display.subworkflow_display

    # AND the innermost node should be included
    assert innermost_node_id in inner_node_event_display.subworkflow_display.node_displays
    innermost_node_event_display = inner_node_event_display.subworkflow_display.node_displays[innermost_node_id]
    assert not innermost_node_event_display.subworkflow_display


def test_get_event_display_context__workflow_output_display_with_none():
    # GIVEN a workflow with a workflow output that is None
    class MyWorkflow(BaseWorkflow):
        class Outputs(BaseWorkflow.Outputs):
            foo = None
            bar = "baz"

    # WHEN we gather the event display context
    display_context = VellumWorkflowDisplay(MyWorkflow).get_event_display_context()

    # THEN the workflow output display should be included
    assert display_context.workflow_outputs.keys() == {"foo", "bar"}
