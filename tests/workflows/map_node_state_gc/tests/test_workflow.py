from tests.workflows.map_node_state_gc.workflow import Inputs, MapNodeStateGCWorkflow


def test_map_node_state_accumulation__verifies_gc():
    """
    Tests whether map node iterations accumulate state or if state is garbage collected.

    This test creates a workflow where each map iteration appends data to the state.
    If state is shared across iterations, we would see accumulating state_sizes.
    If state is isolated per iteration, each iteration should start fresh.
    """

    workflow = MapNodeStateGCWorkflow()

    num_iterations = 100
    items = list(range(num_iterations))

    # WHEN the workflow is run
    terminal_event = workflow.run(inputs=Inputs(items=items))

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    assert len(terminal_event.outputs["results"]) == num_iterations
    assert len(terminal_event.outputs["state_sizes"]) == num_iterations

    state_sizes = terminal_event.outputs["state_sizes"]

    first_state_size = state_sizes[0]
    last_state_size = state_sizes[-1]

    if last_state_size > first_state_size:
        estimated_memory_kb = sum(state_sizes)
        assert False, (
            f"State is accumulating across map node iterations! "
            f"State grew from {first_state_size} to {last_state_size} items. "
            f"Estimated accumulated state memory: ~{estimated_memory_kb} KB. "
            f"This could lead to OOM issues with large datasets."
        )
    else:
        assert all(size == 1 for size in state_sizes), f"Expected all state sizes to be 1, but got: {state_sizes}"


def test_map_node_parent_state_isolation__verifies_independence():
    """
    Tests whether map node iterations have isolated state from each other.

    This verifies that changes to state in one subworkflow iteration don't affect
    other iterations (i.e., each iteration gets its own state copy).
    """

    # GIVEN a workflow with a map node
    workflow = MapNodeStateGCWorkflow()

    # WHEN we run the workflow with multiple iterations
    num_iterations = 10
    terminal_event = workflow.run(inputs=Inputs(items=list(range(num_iterations))))

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    state_sizes = terminal_event.outputs["state_sizes"]

    first_state_size = state_sizes[0]

    if first_state_size == 1 and all(size == 1 for size in state_sizes):
        pass
    else:
        assert False, f"State is being shared across iterations: {state_sizes}"


def test_map_node_memory_profile__large_dataset():
    """
    Tests memory behavior with a larger dataset to simulate real-world OOM scenarios.

    This test helps identify if there are memory leaks or excessive state retention
    that could cause OOM issues in production with large map operations.
    """

    workflow = MapNodeStateGCWorkflow()

    num_iterations = 1000
    terminal_event = workflow.run(inputs=Inputs(items=list(range(num_iterations))))

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    state_sizes = terminal_event.outputs["state_sizes"]

    total_state_items = sum(state_sizes)
    expected_if_gc = num_iterations
    expected_if_no_gc = num_iterations * (num_iterations + 1) // 2

    if total_state_items <= expected_if_gc * 1.1:
        pass
    else:
        if total_state_items >= expected_if_no_gc * 0.9:
            estimated_memory_mb = (total_state_items * 1) / 1024
            assert False, (
                f"State is accumulating across map node iterations! "
                f"Total state items: {total_state_items} (expected ~{expected_if_gc}). "
                f"Estimated memory usage: ~{estimated_memory_mb:.2f} MB. "
                f"This could cause OOM issues with large datasets."
            )
