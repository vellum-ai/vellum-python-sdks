import pytest
from datetime import datetime
import time

from vellum.workflows.events.types import default_serializer

from tests.workflows.basic_emitter_workflow.workflow import BasicEmitterWorkflow, ExampleEmitter, NextNode, StartNode


@pytest.fixture
def mock_datetime_now(mocker):
    def _mock_datetime_now(frozen_datetime):
        mocker.patch("vellum.workflows.events.types.datetime_now", return_value=frozen_datetime)
        mocker.patch("vellum.workflows.state.base.datetime_now", return_value=frozen_datetime)
        return frozen_datetime

    return _mock_datetime_now


def test_run_workflow__happy_path(mock_uuid4_generator, mock_datetime_now):
    # GIVEN a uuid for our state
    state_id_generator = mock_uuid4_generator("vellum.workflows.state.base.uuid4")
    state_id = state_id_generator()
    trace_id = state_id_generator()
    workflow_span_id = state_id_generator()
    start_node_span_id = state_id_generator()
    next_node_span_id = state_id_generator()

    # AND a workflow that uses a custom event emitter
    emitter = ExampleEmitter()
    workflow = BasicEmitterWorkflow(emitters=[emitter])

    # WHEN the workflow is run
    frozen_datetime = datetime(2024, 1, 1, 12, 0, 0)
    mock_datetime_now(frozen_datetime)
    final_event = workflow.run()

    # AND we wait for the emitter to emit all of the events
    time.sleep(0.01)

    # THEN the emitter should have emitted all of the expected events
    base_module = ".".join(__name__.split(".")[:-2])
    events = list(emitter.events)

    assert events[0].name == "workflow.execution.initiated"
    assert events[0].trace_id == trace_id
    assert events[0].span_id == workflow_span_id
    assert events[0].timestamp == frozen_datetime

    assert events[1].name == "node.execution.initiated"
    assert events[1].node_definition == StartNode

    assert events[2].name == "workflow.execution.snapshotted"
    assert default_serializer(events[2].state) == {
        "meta": {
            "id": str(state_id),
            "trace_id": str(trace_id),
            "span_id": str(workflow_span_id),
            "updated_ts": "2024-01-01T12:00:00",
            "workflow_inputs": {},
            "external_inputs": {},
            "node_outputs": {"StartNode.Outputs.final_value": "Hello, World!"},
            "parent": None,
            "node_execution_cache": {
                "node_executions_fulfilled": {f"{base_module}.workflow.StartNode": [str(start_node_span_id)]},
                "node_executions_initiated": {f"{base_module}.workflow.StartNode": [str(start_node_span_id)]},
                "node_executions_queued": {},
                "dependencies_invoked": {},
            },
        },
        "score": 0,
    }

    assert events[3].name == "node.execution.fulfilled"
    assert events[3].node_definition == StartNode
    assert events[3].outputs == {"final_value": "Hello, World!"}

    assert events[4].name == "node.execution.initiated"
    assert events[4].node_definition == NextNode

    assert events[5].name == "workflow.execution.snapshotted"
    assert default_serializer(events[5].state) == {
        "meta": {
            "id": str(state_id),
            "trace_id": str(trace_id),
            "span_id": str(workflow_span_id),
            "updated_ts": "2024-01-01T12:00:00",
            "workflow_inputs": {},
            "external_inputs": {},
            "node_outputs": {
                "StartNode.Outputs.final_value": "Hello, World!",
            },
            "parent": None,
            "node_execution_cache": {
                "node_executions_fulfilled": {
                    f"{base_module}.workflow.StartNode": [str(start_node_span_id)],
                },
                "node_executions_initiated": {
                    f"{base_module}.workflow.StartNode": [str(start_node_span_id)],
                    f"{base_module}.workflow.NextNode": [str(next_node_span_id)],
                },
                "node_executions_queued": {
                    f"{base_module}.workflow.NextNode": [],
                },
                "dependencies_invoked": {
                    str(next_node_span_id): [f"{base_module}.workflow.StartNode"],
                },
            },
        },
        "score": 13,
    }

    assert events[6].name == "workflow.execution.snapshotted"
    assert default_serializer(events[6].state) == {
        "meta": {
            "id": str(state_id),
            "trace_id": str(trace_id),
            "span_id": str(workflow_span_id),
            "updated_ts": "2024-01-01T12:00:00",
            "workflow_inputs": {},
            "external_inputs": {},
            "node_outputs": {
                "StartNode.Outputs.final_value": "Hello, World!",
                "NextNode.Outputs.final_value": "Score: 13",
            },
            "node_execution_cache": {
                "node_executions_fulfilled": {
                    f"{base_module}.workflow.StartNode": [str(start_node_span_id)],
                    f"{base_module}.workflow.NextNode": [str(next_node_span_id)],
                },
                "node_executions_initiated": {
                    f"{base_module}.workflow.StartNode": [str(start_node_span_id)],
                    f"{base_module}.workflow.NextNode": [str(next_node_span_id)],
                },
                "node_executions_queued": {
                    f"{base_module}.workflow.NextNode": [],
                },
                "dependencies_invoked": {
                    str(next_node_span_id): [f"{base_module}.workflow.StartNode"],
                },
            },
            "parent": None,
        },
        "score": 13,
    }

    assert events[7].name == "node.execution.fulfilled"
    assert events[7].node_definition == NextNode
    assert events[7].outputs == {"final_value": "Score: 13"}

    assert events[8].name == "workflow.execution.streaming"
    assert events[8].output.name == "final_value"
    assert events[8].output.value == "Score: 13"

    assert events[9].name == "workflow.execution.fulfilled"
    assert events[9].outputs == {"final_value": "Score: 13"}

    assert len(events) == 10, final_event

    # AND the emitter should have emitted all of the expected state snapshots
    state_snapshots = list(emitter.state_snapshots)
    assert len(state_snapshots) == 3
