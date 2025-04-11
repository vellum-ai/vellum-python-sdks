from vellum.workflows.state.base import BaseState, StateMeta
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.run_from_node.workflow import NextNode, RunFromNodeWorkflow, StartNode


def test_run_workflow__happy_path():
    # GIVEN a workflow that we expect to run from the middle of
    workflow = RunFromNodeWorkflow()

    # WHEN the workflow is run
    terminal_event = workflow.run(
        entrypoint_nodes=[NextNode],
        state=BaseState(
            meta=StateMeta(
                node_outputs={
                    StartNode.Outputs.next_value: 42,
                },
            )
        ),
    )

    # THEN the workflow should be fulfilled
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the final value should be dependent on the intermediate State value
    assert terminal_event.outputs == {"final_value": 43}


def test_stream_workflow__node_inputs():
    # GIVEN a workflow that we expect to run from the middle of
    workflow = RunFromNodeWorkflow()

    # WHEN the workflow is run
    stream = workflow.stream(
        entrypoint_nodes=[NextNode],
        state=BaseState(
            meta=StateMeta(
                node_outputs={
                    StartNode.Outputs.next_value: 42,
                },
            )
        ),
        event_filter=all_workflow_event_filter,
    )
    events = list(stream)

    # THEN the workflow should be fulfilled
    assert events[-1].name == "workflow.execution.fulfilled"

    # AND the node initiated events should have the correct inputs
    node_initiated_event = events[1]
    assert node_initiated_event.name == "node.execution.initiated"
    assert node_initiated_event.inputs == {NextNode.next_value: 42}
