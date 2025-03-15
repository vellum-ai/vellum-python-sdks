from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.basic_inline_prompt_node_validation.workflow import BasicInlinePromptWorkflow, WorkflowInputs


def test_run_workflow__missing_required_input_variable():
    """Confirm that we can successfully invoke a Workflow with a single Inline Prompt Node"""

    # GIVEN a workflow with a missing required input variable
    workflow = BasicInlinePromptWorkflow()

    # WHEN the workflow is run with a missing required input variable
    terminal_event = workflow.run(inputs=WorkflowInputs(noun="color"))

    # THEN the workflow should have rejected
    assert terminal_event.name == "workflow.execution.rejected"

    # AND the error message will be the one defined in the error node
    assert terminal_event.error.message == "Missing required input variables: 'noun'"
    assert terminal_event.error.code == WorkflowErrorCode.INVALID_INPUTS


def test_stream_workflow__missing_required_input_variable():
    """Confirm that we can successfully stream a Workflow with a single Inline Prompt Node"""

    # GIVEN a workflow with a missing required input variable
    workflow = BasicInlinePromptWorkflow()

    # WHEN the workflow is run with a missing required input variable
    terminal_event = workflow.run(inputs=WorkflowInputs(noun="color"))

    # THEN the workflow should have rejected
    assert terminal_event.name == "workflow.execution.rejected"

    # AND the error message will be the one defined in the error node
    assert terminal_event.error.message == "Missing required input variables: 'noun'"
    assert terminal_event.error.code == WorkflowErrorCode.INVALID_INPUTS
