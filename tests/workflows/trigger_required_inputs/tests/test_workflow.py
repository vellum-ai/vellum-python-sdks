from datetime import datetime

from tests.workflows.trigger_required_inputs.workflow import MySchedule, TriggerRequiredInputsWorkflow


def test_trigger_workflow_with_required_inputs_runs_without_inputs_instance():
    workflow = TriggerRequiredInputsWorkflow()
    trigger = MySchedule(current_run_at=datetime.min, next_run_at=datetime.now())

    events = list(workflow.stream(trigger=trigger))

    assert events[-1].name == "workflow.execution.fulfilled"
