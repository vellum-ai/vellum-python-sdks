from datetime import datetime, timedelta

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
