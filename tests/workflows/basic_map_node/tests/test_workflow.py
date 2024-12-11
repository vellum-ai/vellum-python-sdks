from vellum.workflows.events import NodeExecutionFulfilledEvent
from vellum.workflows.events.types import CodeResourceDefinition, NodeParentContext, WorkflowParentContext
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.basic_map_node.workflow import Inputs, IterationSubworkflow, SimpleMapExample


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
    assert terminal_event.parent is None


def test_map_node_streaming_events():
    """
    Ensure that we can stream the events of a Workflow that contains a MapNode,
    with a particular focus on ensuring that the events and their parent contexts are correct.
    """
    # GIVEN a workflow with a map node
    workflow = SimpleMapExample()

    # WHEN we stream the workflow events
    events = list(workflow.stream(inputs=Inputs(fruits=["apple", "banana"]), event_filter=all_workflow_event_filter))

    # THEN we see the expected events in the correct relative order
    workflow_initiated_events = [e for e in events if e.name == "workflow.execution.initiated"]
    node_events = [e for e in events if e.name.startswith("node.")]
    workflow_fulfilled_events = [e for e in events if e.name == "workflow.execution.fulfilled"]
    workflow_snapshotted_events = [e for e in events if e.name == "workflow.execution.snapshotted"]

    # Main workflow initiated event
    assert workflow_initiated_events[0].workflow_definition == SimpleMapExample
    assert workflow_initiated_events[0].parent is None

    # Subworkflow initiated events
    assert len(workflow_initiated_events) == 3  # Main + 2 subworkflows
    for event in workflow_initiated_events[1:]:
        assert event.workflow_definition == IterationSubworkflow
        assert event.parent is not None
        assert event.parent.type == "WORKFLOW_NODE"
        assert event.parent.parent is not None
        assert event.parent.parent.type == "WORKFLOW"
        assert event.parent.parent.workflow_definition == CodeResourceDefinition.encode(SimpleMapExample)

    # Node events
    assert len(node_events) == 6  # 2 initiated + 2 fulfilled + 2 others

    # Node initiated events
    node_initiated = [e for e in node_events if e.name == "node.execution.initiated"]
    assert node_initiated[0].parent is not None
    assert node_initiated[0].parent.type == "WORKFLOW"
    assert node_initiated[0].parent.workflow_definition == CodeResourceDefinition.encode(SimpleMapExample)

    # Node fulfilled events
    node_fulfilled = [e for e in node_events if e.name == "node.execution.fulfilled"]
    node_fulfilled = sorted(
        node_fulfilled,
        key=lambda output: (
            sum(output.outputs.count) if isinstance(output.outputs.count, list) else output.outputs.count
        ),
    )
    assert len(node_fulfilled) == 3
    # Check first iteration
    first_event = node_fulfilled[0]
    assert isinstance(first_event, NodeExecutionFulfilledEvent)
    assert first_event.outputs.count == len("apple")  # 5
    assert first_event.parent is not None
    assert isinstance(first_event.parent, WorkflowParentContext)
    assert first_event.parent.type == "WORKFLOW"
    assert first_event.parent.workflow_definition == CodeResourceDefinition.encode(IterationSubworkflow)

    parent_node = first_event.parent.parent
    assert parent_node is not None
    assert isinstance(parent_node, NodeParentContext)
    assert parent_node.type == "WORKFLOW_NODE"

    parent_workflow = parent_node.parent
    assert parent_workflow is not None
    assert isinstance(parent_workflow, WorkflowParentContext)
    assert parent_workflow.type == "WORKFLOW"
    assert parent_workflow.workflow_definition == CodeResourceDefinition.encode(SimpleMapExample)

    # Check second iteration
    second_event = node_fulfilled[1]
    assert isinstance(second_event, NodeExecutionFulfilledEvent)
    assert second_event.outputs.count == len("banana") + 1
    assert second_event.parent is not None
    assert isinstance(second_event.parent, WorkflowParentContext)
    assert second_event.parent.type == "WORKFLOW"
    assert second_event.parent.workflow_definition == CodeResourceDefinition.encode(IterationSubworkflow)

    parent_node = second_event.parent.parent
    assert parent_node is not None
    assert isinstance(parent_node, NodeParentContext)
    assert parent_node.type == "WORKFLOW_NODE"

    parent_workflow = parent_node.parent
    assert parent_workflow is not None
    assert isinstance(parent_workflow, WorkflowParentContext)
    assert parent_workflow.type == "WORKFLOW"
    assert parent_workflow.workflow_definition == CodeResourceDefinition.encode(SimpleMapExample)

    # Workflow fulfilled events
    assert len(workflow_fulfilled_events) == 3  # Main + 2 subworkflows
    assert workflow_fulfilled_events[-1].outputs == {"final_value": [5, 7]}
    assert workflow_fulfilled_events[-1].parent is None

    # Workflow snapshotted events
    assert len(workflow_snapshotted_events) > 0
