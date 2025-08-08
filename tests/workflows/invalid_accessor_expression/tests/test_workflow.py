from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    AdHocExecutePromptEvent,
    FulfilledAdHocExecutePromptEvent,
    FunctionCall,
    FunctionCallVellumValue,
    InitiatedAdHocExecutePromptEvent,
    PromptOutput,
)
from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.invalid_accessor_expression.workflow import InvalidAccessorExpressionWorkflow


def test_run_workflow__happy_path(vellum_adhoc_prompt_client):
    # GIVEN a workflow that has an invalid node
    workflow = InvalidAccessorExpressionWorkflow()

    # AND we mock the prompt response to return a FunctionCallVellumValue without the expected field
    expected_outputs: List[PromptOutput] = [
        FunctionCallVellumValue(value=FunctionCall(name="test_function", arguments={"existing_field": "value"})),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[AdHocExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[AdHocExecutePromptEvent] = [
            InitiatedAdHocExecutePromptEvent(execution_id=execution_id),
            FulfilledAdHocExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN the workflow should have completed with a failure
    assert terminal_event.name == "workflow.execution.rejected", terminal_event

    # AND the outputs should be defaulted correctly
    assert terminal_event.error.code == WorkflowErrorCode.INVALID_INPUTS, terminal_event.error.message
    assert "Field 'no_value' not found on BaseModel FunctionCallVellumValue" == terminal_event.error.message
