from datetime import datetime, timedelta

from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.scheduled_trigger_execution.workflows.multi_port_workflow import (
    Inputs as MultiPortInputs,
    MultiPortScheduledWorkflow,
    MySchedule as MultiPortSchedule,
)
from tests.workflows.scheduled_trigger_execution.workflows.simple_workflow import MySchedule, SimpleScheduledWorkflow


def test_workflow_initiated_event_has_trigger():
    # GIVEN a simple workflow using ScheduleTrigger
    workflow = SimpleScheduledWorkflow()
    trigger = MySchedule(current_run_at=datetime.now(), next_run_at=datetime.now() + timedelta(minutes=1))

    # WHEN streaming events
    events = list(workflow.stream(trigger=trigger))

    # THEN the first event is workflow.execution.initiated
    assert len(events) >= 1
    initiated = events[0]
    assert initiated.name == "workflow.execution.initiated"

    # AND the initiated event has the trigger field
    trigger_definition = initiated.body.trigger
    assert trigger_definition is not None
    assert trigger_definition.__name__ == "MySchedule"


def test_multi_port_node_executes_once_with_trigger():
    """
    Tests that a node with multiple ports only executes once when running with a trigger.

    This is a regression test for APO-2387 where nodes with multiple ports were being
    executed multiple times because the entrypoints were not deduplicated.
    """
    # GIVEN a workflow with a trigger pointing to a node with multiple ports
    workflow = MultiPortScheduledWorkflow()
    trigger = MultiPortSchedule(current_run_at=datetime.now(), next_run_at=datetime.now() + timedelta(minutes=1))
    inputs = MultiPortInputs(value="test")

    # WHEN streaming events
    events = list(workflow.stream(inputs=inputs, trigger=trigger, event_filter=all_workflow_event_filter))

    # THEN the MultiPortNode should only have one initiated event
    node_initiated_events = [e for e in events if e.name == "node.execution.initiated"]
    multi_port_node_events = [e for e in node_initiated_events if e.node_definition.__name__ == "MultiPortNode"]
    assert (
        len(multi_port_node_events) == 1
    ), f"Expected MultiPortNode to execute once, but found {len(multi_port_node_events)} executions"

    # AND the workflow should complete successfully
    assert events[-1].name == "workflow.execution.fulfilled"
