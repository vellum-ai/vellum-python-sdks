from tests.workflows.basic_map_node_annotation.workflow import Inputs, SimpleMapExample


def test_run_workflow__happy_path():
    # GIVEN a workflow that references a Map example
    workflow = SimpleMapExample()

    # WHEN the workflow is run
    terminal_event = workflow.run(inputs=Inputs(fruits=["apple", "banana", "date"]))

    apple_len, banana_len, date_len = len("apple"), len("banana"), len("date")
    apple_index, banana_index, date_index = 0, 1, 2
    apple_final_value, banana_final_value, date_final_value = (
        apple_len + apple_index,
        banana_len + banana_index,
        date_len + date_index,
    )

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the output should match the mapped items
    assert terminal_event.outputs == {"final_value": [apple_final_value, banana_final_value, date_final_value]}
