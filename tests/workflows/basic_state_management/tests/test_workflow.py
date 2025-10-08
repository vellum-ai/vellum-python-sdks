from tests.workflows.basic_state_management.workflow import BasicStateManagement, State


def test_run_workflow__happy_path():
    # GIVEN a workflow that uses State with a derived value and writable value
    workflow = BasicStateManagement()

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow should be fulfilled
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the final value should be read from the written state
    assert terminal_event.outputs == {"final_value": 3}

    # AND the final state should contain the written value
    assert terminal_event.final_state is not None
    assert isinstance(terminal_event.final_state, State)
    assert terminal_event.final_state.writable_value == 3
