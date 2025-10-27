import gc
import tracemalloc

from tests.workflows.map_node_state_gc.workflow import Inputs, MapNodeStateGCWorkflow, State


def test_map_node_does_not_garbage_collect_nested_states():
    """
    Demonstrates that nested subworkflow states are NOT garbage collected.

    This test shows that after map node execution, nested State objects
    from individual iterations remain in memory, causing a memory leak.
    """

    gc.collect()
    tracemalloc.start()

    initial_state_count = len([obj for obj in gc.get_objects() if isinstance(obj, State)])
    baseline_memory = tracemalloc.get_traced_memory()[0]

    workflow = MapNodeStateGCWorkflow()
    num_iterations = 50

    terminal_event = workflow.run(inputs=Inputs(items=list(range(num_iterations))))

    assert terminal_event.name == "workflow.execution.fulfilled"

    gc.collect()

    final_state_count = len([obj for obj in gc.get_objects() if isinstance(obj, State)])
    final_memory = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()

    state_growth = final_state_count - initial_state_count
    memory_growth = (final_memory - baseline_memory) / 1024  # KB

    max_acceptable_state_growth = 5

    expected_output_memory_kb = (num_iterations * 1000) / 1024  # ~50KB
    max_acceptable_memory_kb = expected_output_memory_kb * 5  # ~250KB with overhead

    assert state_growth > max_acceptable_state_growth, (
        f"Expected state growth >{max_acceptable_state_growth} to demonstrate leak, "
        f"but got {state_growth}. If this passes, the leak may have been fixed!"
    )

    assert memory_growth > max_acceptable_memory_kb, (
        f"Expected memory growth >{max_acceptable_memory_kb:.2f}KB to demonstrate leak, "
        f"but got {memory_growth:.2f}KB. If this passes, the leak may have been fixed!"
    )
