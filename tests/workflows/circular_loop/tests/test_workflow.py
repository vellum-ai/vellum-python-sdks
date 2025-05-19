import pytest

from vellum.workflows.types.core import MergeBehavior

from tests.workflows.circular_loop.workflow import CircularLoopWorkflow, TopNode


def test_workflow__happy_path():
    """
    This test is not happy now.

    The key problem is:
    1. TopNode after IncrementCounterNode will not be executed
    2. This breaks the loop and the workflow terminates prematurely
    """
    workflow = CircularLoopWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event.body

    assert terminal_event.outputs.counter == 2
    assert terminal_event.outputs.completed is True


def test_workflow__top_node_awaits_any():
    """
    This test solves the same problem as the previous test, but considers the case where the TopNode
    uses an AWAIT ANY merge behavior.

    The key problem is:
    1. TopNode after IncrementCounterNode will not be executed
    2. This breaks the loop and the workflow terminates prematurely
    """

    # GIVEN a workflow with a TopNode that uses an AWAIT ANY merge behavior
    workflow = CircularLoopWorkflow()
    TopNode.Trigger.merge_behavior = MergeBehavior.AWAIT_ANY

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN the workflow terminates successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event.body

    # AND the outputs are as expected
    assert terminal_event.outputs.counter == 2
    assert terminal_event.outputs.completed is True

    # AND we cleanup the changes
    TopNode.Trigger.merge_behavior = MergeBehavior.AWAIT_ATTRIBUTES
