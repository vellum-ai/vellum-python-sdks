from vellum.workflows.constants import undefined
from vellum.workflows.workflows.event_filters import root_workflow_event_filter

from tests.workflows.basic_conditional_branch.workflow import (
    BasicConditionalBranchWorkflow,
    BranchANode,
    Inputs,
    StartNode,
)


def test_run_workflow__branch_a():
    """
    Ensure that a Workflow can successfully invoke the `if` branch.
    """

    # GIVEN a Workflow that uses a Conditional Branch
    workflow = BasicConditionalBranchWorkflow()

    # WHEN we run the Workflow with a `True` value
    terminal_event = workflow.run(inputs=Inputs(value=True))

    # THEN the Workflow should succeed with the expected outputs
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event
    assert terminal_event.outputs.branch_a == "Branch A"
    assert terminal_event.outputs.branch_b is undefined


def test_run_workflow__branch_b():
    """
    Ensure that a Workflow can successfully invoke the `else` branch.
    """

    # GIVEN a Workflow that uses a Conditional Branch
    workflow = BasicConditionalBranchWorkflow()

    # WHEN we run the Workflow with a `False` value
    terminal_event = workflow.run(inputs=Inputs(value=False))

    # THEN the Workflow should succeed with the expected outputs
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event
    assert terminal_event.outputs.branch_b == "Branch B"
    assert terminal_event.outputs.branch_a is undefined


def test_stream_workflow__verify_invoked_ports():
    """
    Ensure that a Workflow can successfully stream invoked ports in its node events.
    """

    # GIVEN a Workflow that uses a Conditional Branch
    workflow = BasicConditionalBranchWorkflow()

    # WHEN we stream the Workflow
    stream = workflow.stream(
        inputs=Inputs(value=True),
        event_filter=root_workflow_event_filter,
    )
    events = list(stream)

    # THEN we should see the invoked ports in the node events
    node_fulfilled_events = [event for event in events if event.name == "node.execution.fulfilled"]
    assert len(node_fulfilled_events) == 2
    assert node_fulfilled_events[0].invoked_ports == {StartNode.Ports.branch_a}
    assert node_fulfilled_events[1].invoked_ports == {BranchANode.Ports.default}
