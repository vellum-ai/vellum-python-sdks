import gc
import tracemalloc

from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.state.store import EmptyStore

from tests.workflows.map_node_state_gc.workflow import Inputs, MapNodeStateGCWorkflow, State


def test_map_node_does_not_garbage_collect_nested_states():
    """
    Verifies that nested subworkflow states ARE garbage collected.

    This test ensures that after map node execution, nested State objects
    from individual iterations are properly released from memory.
    """

    gc.collect()
    tracemalloc.start()

    initial_state_count = len([obj for obj in gc.get_objects() if isinstance(obj, State)])
    baseline_memory = tracemalloc.get_traced_memory()[0]

    context = WorkflowContext(store_class=EmptyStore)
    workflow = MapNodeStateGCWorkflow(context=context)
    num_iterations = 50

    terminal_event = workflow.run(inputs=Inputs(items=list(range(num_iterations))))

    assert terminal_event.name == "workflow.execution.fulfilled"

    del terminal_event
    del workflow

    for _ in range(5):
        gc.collect()

    final_state_count = len([obj for obj in gc.get_objects() if isinstance(obj, State)])
    final_memory = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()

    state_growth = final_state_count - initial_state_count
    memory_growth = (final_memory - baseline_memory) / 1024  # KB

    max_acceptable_state_growth = 5

    expected_output_memory_kb = (num_iterations * 1000) / 1024  # ~50KB
    max_acceptable_memory_kb = expected_output_memory_kb * 40  # ~2MB with workflow overhead

    assert state_growth <= max_acceptable_state_growth, (
        f"Memory leak detected! State objects grew by {state_growth} (expected <={max_acceptable_state_growth}). "
        f"Nested states are NOT being garbage collected."
    )

    assert memory_growth <= max_acceptable_memory_kb, (
        f"Memory leak detected! Memory grew by {memory_growth:.2f}KB (expected <={max_acceptable_memory_kb:.2f}KB). "
        f"Nested states are NOT being garbage collected."
    )
