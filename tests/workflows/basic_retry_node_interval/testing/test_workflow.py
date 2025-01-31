from datetime import datetime, timedelta

from tests.workflows.basic_retry_node_interval.workflow import SimpleRetryExample


def test_run_workflow__happy_path():
    # GIVEN a workflow that references a Retry example with interval
    workflow = SimpleRetryExample()

    # WHEN the workflow is run
    datetime_start = datetime.now()
    terminal_event = workflow.run()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the output should match the environment variable
    assert terminal_event.outputs == {"final_value": 3}

    # AND the duration should be (retry - 1) * interval
    assert terminal_event.timestamp - datetime_start > timedelta(seconds=0.2)
