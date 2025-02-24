import pytest
from typing import Union

from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.workflows.base import BaseWorkflow

from tests.workflows.basic_external_input.workflow import BasicInputNodeWorkflow, InputNode


def test_workflow__happy_path_multi_stop():
    """
    Runs the non-streamed execution of a Workflow with a single Nodes defining ExternalInputs.
    """

    # GIVEN a workflow that uses an Input Node
    workflow = BasicInputNodeWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN we should get workflow in PAUSED state
    assert terminal_event.name == "workflow.execution.paused"
    external_inputs = list(terminal_event.external_inputs)

    assert InputNode.ExternalInputs.message == external_inputs[0]
    assert len(external_inputs) == 1

    # WHEN we resume the workflow
    final_terminal_event = workflow.run(
        external_inputs={
            InputNode.ExternalInputs.message: "sunny",
        },
    )

    # THEN we should get workflow in FULFILLED state
    assert final_terminal_event.name == "workflow.execution.fulfilled"
    assert final_terminal_event.outputs.final_value == "sunny"


def test_workflow__happy_path_multi_stop_invalid_external_input():
    """
    Runs the non-streamed execution of a Workflow with a single Nodes defining ExternalInputs.
    """

    # GIVEN a workflow that uses an Input Node
    workflow = BasicInputNodeWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN we should get workflow in PAUSED state
    assert terminal_event.name == "workflow.execution.paused"
    external_inputs = list(terminal_event.external_inputs)

    assert InputNode.ExternalInputs.message == external_inputs[0]
    assert len(external_inputs) == 1

    # WHEN we resume the workflow with invalid external input
    with pytest.raises(NodeException) as exc_info:
        final_terminal_event = workflow.run(  # noqa: F841
            external_inputs={
                InputNode.ExternalInputs.message: 12,
            },
        )

    # THEN we should get a rejected workflow event with the correct error
    assert "Invalid external input type for message" == str(exc_info.value)


def test_workflow__happy_path_multi_stop_union_type():
    """
    Runs the non-streamed execution of a Workflow with a single Nodes defining ExternalInputs.
    """

    class InputNode(BaseNode):
        class ExternalInputs(BaseNode.ExternalInputs):
            message: Union[str, int]

    class TestWorkflow(BaseWorkflow):
        graph = InputNode

        class Outputs(BaseWorkflow.Outputs):
            final_value = InputNode.ExternalInputs.message

    # GIVEN a workflow that uses an Input Node
    workflow = TestWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN we should get workflow in PAUSED state
    assert terminal_event.name == "workflow.execution.paused"
    external_inputs = list(terminal_event.external_inputs)

    assert InputNode.ExternalInputs.message == external_inputs[0]
    assert len(external_inputs) == 1

    # WHEN we resume the workflow with valid external input
    final_terminal_event = workflow.run(
        external_inputs={
            InputNode.ExternalInputs.message: "hello",
        },
    )

    # THEN we should get a fulfilled workflow event
    assert final_terminal_event.name == "workflow.execution.fulfilled"

    # WHEN we resume the workflow with valid external input
    final_terminal_event = workflow.run(
        external_inputs={
            InputNode.ExternalInputs.message: 12,
        },
    )

    # THEN we should get a fulfilled workflow event
    assert final_terminal_event.name == "workflow.execution.fulfilled"

    # WHEN we resume the workflow with invalid external input
    with pytest.raises(NodeException) as exc_info:
        final_terminal_event = workflow.run(  # noqa: F841
            external_inputs={
                InputNode.ExternalInputs.message: [1, 2, 3],
            },
        )

    # THEN we should get a rejected workflow event with the correct error
    assert "Invalid external input type for message" == str(exc_info.value)
