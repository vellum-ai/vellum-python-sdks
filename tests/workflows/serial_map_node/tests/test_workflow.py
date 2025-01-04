from tests.workflows.serial_map_node.workflow import Inputs, SerialMapExample


def test_run_workflow__happy_path():
    # GIVEN a workflow that references a Map example with a max concurrency of 1
    workflow = SerialMapExample()

    # WHEN the workflow is run
    terminal_event = workflow.run(inputs=Inputs(fruits=["apple", "banana", "cherry"]))

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the output should match the mapped items
    assert terminal_event.outputs == {"final_value": ["apple apple", "banana banana", "cherry cherry"]}
