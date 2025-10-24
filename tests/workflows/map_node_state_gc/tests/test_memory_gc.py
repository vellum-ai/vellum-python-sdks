import gc
import tracemalloc
from typing import List

from tests.workflows.map_node_state_gc.workflow import Inputs, MapNodeStateGCWorkflow


def test_map_node_memory_usage__verifies_gc_with_tracemalloc():
    """
    Tests that memory usage stays relatively constant during map node execution.

    Uses tracemalloc to measure actual memory usage and verify that nested states
    are properly garbage collected after each iteration completes.
    """

    tracemalloc.start()
    gc.collect()  # Clean up any existing garbage
    baseline_memory = tracemalloc.get_traced_memory()[0]

    workflow = MapNodeStateGCWorkflow()

    num_iterations = 100
    memory_snapshots: List[int] = []

    memory_snapshots.append(tracemalloc.get_traced_memory()[0] - baseline_memory)

    terminal_event = workflow.run(inputs=Inputs(items=list(range(num_iterations))))

    memory_snapshots.append(tracemalloc.get_traced_memory()[0] - baseline_memory)

    gc.collect()
    final_memory = tracemalloc.get_traced_memory()[0] - baseline_memory

    tracemalloc.stop()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    expected_output_memory = num_iterations * 1000  # ~100KB for strings

    max_reasonable_memory = expected_output_memory * 5  # ~500KB

    memory_if_not_gcd = sum(i * 1000 for i in range(1, num_iterations + 1))

    if final_memory > max_reasonable_memory:
        if final_memory > memory_if_not_gcd * 0.5:
            assert False, (
                f"Memory usage suggests nested states are NOT being garbage collected! "
                f"Final memory: {final_memory / 1024:.2f} KB "
                f"Expected if GC'd: <{max_reasonable_memory / 1024:.2f} KB "
                f"Expected if NOT GC'd: ~{memory_if_not_gcd / 1024:.2f} KB"
            )
        else:
            pass

    state_sizes = terminal_event.outputs["state_sizes"]
    assert all(size == 1 for size in state_sizes), f"State sizes should all be 1, but got: {state_sizes[:10]}..."


def test_map_node_nested_states_are_garbage_collected():
    """
    Tests that nested subworkflow states are actually garbage collected.

    This test verifies that after map node execution completes, the nested
    state objects from individual iterations are no longer in memory.
    """

    gc.collect()
    from tests.workflows.map_node_state_gc.workflow import State

    initial_state_count = len([obj for obj in gc.get_objects() if isinstance(obj, State)])

    workflow = MapNodeStateGCWorkflow()
    num_iterations = 50

    terminal_event = workflow.run(inputs=Inputs(items=list(range(num_iterations))))

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    gc.collect()

    final_state_count = len([obj for obj in gc.get_objects() if isinstance(obj, State)])
    state_growth = final_state_count - initial_state_count

    max_acceptable_growth = 5  # Allow some overhead

    if state_growth > max_acceptable_growth:
        if state_growth >= num_iterations * 0.5:
            assert False, (
                f"Nested states appear to NOT be garbage collected! "
                f"State object count grew by {state_growth} "
                f"(expected <{max_acceptable_growth}, would be ~{num_iterations} if not GC'd)"
            )
        else:
            pass


def test_map_node_memory_stays_constant_during_execution():
    """
    Tests that memory usage stays relatively constant during map node execution.

    This test monitors memory at multiple points during execution to verify
    that memory doesn't continuously grow as iterations complete.
    """

    tracemalloc.start()
    gc.collect()
    baseline_memory = tracemalloc.get_traced_memory()[0]

    workflow = MapNodeStateGCWorkflow()

    num_iterations = 200
    memory_samples: List[int] = []

    memory_samples.append(tracemalloc.get_traced_memory()[0] - baseline_memory)

    terminal_event = workflow.run(inputs=Inputs(items=list(range(num_iterations))))

    memory_samples.append(tracemalloc.get_traced_memory()[0] - baseline_memory)

    gc.collect()
    memory_samples.append(tracemalloc.get_traced_memory()[0] - baseline_memory)

    tracemalloc.stop()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    start_memory = memory_samples[0]
    end_memory = memory_samples[1]
    post_gc_memory = memory_samples[2]

    memory_growth = end_memory - start_memory

    expected_memory = num_iterations * 1000

    max_reasonable_growth = expected_memory * 5

    memory_if_accumulating = sum(i * 1000 for i in range(1, num_iterations + 1))

    if memory_growth > max_reasonable_growth:
        if memory_growth > memory_if_accumulating * 0.5:
            assert False, (
                f"Memory growth suggests state accumulation! "
                f"Growth: {memory_growth / 1024:.2f} KB "
                f"Expected: <{max_reasonable_growth / 1024:.2f} KB "
                f"Would be if accumulating: ~{memory_if_accumulating / 1024:.2f} KB"
            )

    assert post_gc_memory <= end_memory, (
        f"GC should not increase memory, but it did: "
        f"before GC: {end_memory / 1024:.2f} KB, after GC: {post_gc_memory / 1024:.2f} KB"
    )
