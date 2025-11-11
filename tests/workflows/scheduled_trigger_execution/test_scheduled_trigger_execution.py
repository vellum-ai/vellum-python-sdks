from datetime import datetime, timedelta

from tests.workflows.scheduled_trigger_execution.workflows.simple_workflow import MySchedule, SimpleScheduledWorkflow


def test_workflow_initiated_event_has_scheduled_trigger_parent_context():
    # GIVEN a simple workflow using ScheduleTrigger
    workflow = SimpleScheduledWorkflow()
    trigger = MySchedule(current_run_at=datetime.now(), next_run_at=datetime.now() + timedelta(minutes=1))

    # WHEN streaming events
    events = list(workflow.stream(trigger=trigger))

    # THEN the first event is workflow.execution.initiated
    assert len(events) >= 1
    initiated = events[0]
    assert initiated.name == "workflow.execution.initiated"

    # AND the initiated parent context is of type scheduled
    assert initiated.parent is not None
    assert initiated.parent.type == "SCHEDULED"

    # AND the trigger_id matches the trigger class id
    assert getattr(initiated.parent, "trigger_id", None) == MySchedule.__id__  # type: ignore[attr-defined]

    # AND the trigger_definition is present
    trigger_def = getattr(initiated.parent, "trigger_definition", None)  # type: ignore[attr-defined]
    assert trigger_def is not None
    assert trigger_def.name == "MySchedule"
    assert trigger_def.module == ["tests", "workflows", "scheduled_trigger_execution", "workflows", "simple_workflow"]

    # AND the final event should fulfill
    assert events[-1].name == "workflow.execution.fulfilled"
