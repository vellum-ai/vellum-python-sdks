from vellum.workflows.events import NodeExecutionFulfilledEvent
from vellum.workflows.events.types import NodeParentContext, VellumCodeResourceDefinition, WorkflowParentContext
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.basic_map_node.workflow import Inputs, Iteration, IterationSubworkflow, SimpleMapExample


def test_run_workflow__happy_path():
    # GIVEN a workflow that references a Map example
    workflow = SimpleMapExample()

    # WHEN the workflow is run
    terminal_event = workflow.run(inputs=Inputs(fruits=["apple", "banana", "date"]))

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the output should match the mapped items
    assert terminal_event.outputs == {"final_value": [5, 7, 6]}

    # Assert that parent is a valid field, for now empty
    assert terminal_event.parent is not None
    assert terminal_event.parent.type == "EXTERNAL"


def test_map_node_streaming_events():
    """
    Ensure that we can stream the events of a Workflow that contains a MapNode,
    with a particular focus on ensuring that the events and their parent contexts are correct.
    """
    # GIVEN a workflow with a map node
    workflow = SimpleMapExample()

    # WHEN we stream the workflow events
    events = list(workflow.stream(inputs=Inputs(fruits=["apple", "banana"]), event_filter=all_workflow_event_filter))

    apple_len, banana_len = len("apple"), len("banana")
    apple_index, banana_index = 0, 1
    apple_final_value, banana_final_value = apple_len + apple_index, banana_len + banana_index

    # THEN we see the expected events in the correct relative order
    workflow_initiated_events = [e for e in events if e.name == "workflow.execution.initiated"]
    node_initiated = [e for e in events if e.name == "node.execution.initiated"]
    node_fulfilled = [e for e in events if e.name == "node.execution.fulfilled"]
    node_streaming = [e for e in events if e.name == "node.execution.streaming"]
    workflow_fulfilled_events = [e for e in events if e.name == "workflow.execution.fulfilled"]
    workflow_snapshotted_events = [e for e in events if e.name == "workflow.execution.snapshotted"]

    # Main workflow initiated event
    assert workflow_initiated_events[0].workflow_definition == SimpleMapExample
    assert workflow_initiated_events[0].parent is not None
    assert workflow_initiated_events[0].parent.type == "EXTERNAL"

    # Subworkflow initiated events
    assert len(workflow_initiated_events) == 3  # Main + 2 subworkflows
    for event in workflow_initiated_events[1:]:
        assert event.workflow_definition == IterationSubworkflow
        assert event.parent is not None
        assert event.parent.type == "WORKFLOW_NODE"
        assert event.parent.parent is not None
        assert event.parent.parent.type == "WORKFLOW"
        assert event.parent.parent.workflow_definition == VellumCodeResourceDefinition.encode(SimpleMapExample)

    # Node initiated events
    assert len(node_initiated) == 3
    assert node_initiated[0].parent is not None
    assert node_initiated[0].parent.type == "WORKFLOW"
    assert node_initiated[0].parent.workflow_definition == VellumCodeResourceDefinition.encode(SimpleMapExample)
    first_iteration_span_id = next(e.span_id for e in node_initiated if e.inputs.get(Iteration.index) == 0)
    second_iteration_span_id = next(e.span_id for e in node_initiated if e.inputs.get(Iteration.index) == 1)

    # Node fulfilled events
    assert len(node_fulfilled) == 3

    # Check first iteration
    first_event = next(e for e in node_fulfilled if e.span_id == first_iteration_span_id)
    assert isinstance(first_event, NodeExecutionFulfilledEvent)
    assert first_event.outputs.count == apple_final_value
    assert first_event.parent is not None
    assert isinstance(first_event.parent, WorkflowParentContext)
    assert first_event.parent.type == "WORKFLOW"
    assert first_event.parent.workflow_definition == VellumCodeResourceDefinition.encode(IterationSubworkflow)

    parent_node = first_event.parent.parent
    assert parent_node is not None
    assert isinstance(parent_node, NodeParentContext)
    assert parent_node.type == "WORKFLOW_NODE"

    parent_workflow = parent_node.parent
    assert parent_workflow is not None
    assert isinstance(parent_workflow, WorkflowParentContext)
    assert parent_workflow.type == "WORKFLOW"
    assert parent_workflow.workflow_definition == VellumCodeResourceDefinition.encode(SimpleMapExample)

    # Check second iteration
    second_event = next(e for e in node_fulfilled if e.span_id == second_iteration_span_id)
    assert isinstance(second_event, NodeExecutionFulfilledEvent)
    assert second_event.outputs.count == banana_final_value
    assert second_event.parent is not None
    assert isinstance(second_event.parent, WorkflowParentContext)
    assert second_event.parent.type == "WORKFLOW"
    assert second_event.parent.workflow_definition == VellumCodeResourceDefinition.encode(IterationSubworkflow)

    parent_node = second_event.parent.parent
    assert parent_node is not None
    assert isinstance(parent_node, NodeParentContext)
    assert parent_node.type == "WORKFLOW_NODE"

    parent_workflow = parent_node.parent
    assert parent_workflow is not None
    assert isinstance(parent_workflow, WorkflowParentContext)
    assert parent_workflow.type == "WORKFLOW"
    assert parent_workflow.workflow_definition == VellumCodeResourceDefinition.encode(SimpleMapExample)

    # Workflow fulfilled events
    assert len(workflow_fulfilled_events) == 3  # Main + 2 subworkflows
    assert workflow_fulfilled_events[-1].outputs == {"final_value": [apple_final_value, banana_final_value]}
    assert workflow_fulfilled_events[-1].parent is not None
    assert workflow_fulfilled_events[-1].parent.type == "EXTERNAL"

    # Workflow snapshotted events
    assert len(workflow_snapshotted_events) > 0

    # Node streaming events
    assert len(node_streaming) == 6  # 1 for the output initiating, 2 for each item, 1 for the fulfilled output

    assert node_streaming[0].output.is_initiated
    assert node_streaming[0].output.name == "count"

    assert node_streaming[1].output.is_streaming
    assert node_streaming[1].output.name == "count"
    assert node_streaming[2].output.is_streaming
    assert node_streaming[2].output.name == "count"
    assert node_streaming[3].output.is_streaming
    assert node_streaming[3].output.name == "count"
    assert node_streaming[4].output.is_streaming
    assert node_streaming[4].output.name == "count"

    assert {
        node_streaming[1].output.delta,
        node_streaming[2].output.delta,
        node_streaming[3].output.delta,
        node_streaming[4].output.delta,
    } == {
        (None, 0, "INITIATED"),
        (None, 1, "INITIATED"),
        (apple_final_value, 0, "FULFILLED"),
        (banana_final_value, 1, "FULFILLED"),
    }

    assert node_streaming[5].output.is_fulfilled
    assert node_streaming[5].output.name == "count"
    assert node_streaming[5].output.value == [apple_final_value, banana_final_value]
