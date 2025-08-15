from datetime import datetime, timedelta

from tests.workflows.subworkflow_concurrency_limit.workflow import SubworkflowConcurrencyLimitWorkflow


def test_subworkflow_concurrency_limit__happy_path():
    """
    Tests that only 2 subworkflow deployment nodes can run concurrently.
    """

    workflow = SubworkflowConcurrencyLimitWorkflow()

    datetime_start = datetime.now()
    terminal_event = workflow.run()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    execution_times = terminal_event.outputs.execution_times
    assert len(execution_times) == 4

    execution_times.sort()

    time_diff_first_two = execution_times[1] - execution_times[0]
    assert (
        time_diff_first_two < 0.05
    ), f"First two nodes should start nearly simultaneously, but diff was {time_diff_first_two}"

    time_diff_to_third = execution_times[2] - execution_times[0]
    assert (
        time_diff_to_third > 0.15
    ), f"Third node should start after first batch completes, but diff was {time_diff_to_third}"

    time_diff_to_fourth = execution_times[3] - execution_times[0]
    assert (
        time_diff_to_fourth > 0.15
    ), f"Fourth node should start after first batch completes, but diff was {time_diff_to_fourth}"

    total_runtime = datetime.now() - datetime_start
    assert total_runtime > timedelta(seconds=0.4), f"Total runtime should be at least 400ms, but was {total_runtime}"


def test_subworkflow_concurrency_with_general_concurrency__happy_path():
    """
    Tests that general concurrency control takes precedence over subworkflow concurrency.
    """

    workflow = SubworkflowConcurrencyLimitWorkflow()

    datetime_start = datetime.now()
    terminal_event = workflow.run(max_concurrency=1)

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    total_runtime = datetime.now() - datetime_start
    assert total_runtime > timedelta(
        seconds=0.8
    ), f"With max_concurrency=1, runtime should be at least 800ms, but was {total_runtime}"

    execution_times = terminal_event.outputs.execution_times
    assert len(execution_times) == 4
