from uuid import uuid4
from typing import Any, Iterator

from vellum import ExecutePromptEvent, InitiatedExecutePromptEvent

from tests.workflows.basic_inline_prompt_node_timeout.workflow import BasicInlinePromptWorkflow, WorkflowInputs


def test_prompt_timeout_setting(vellum_adhoc_prompt_client):
    """Test that timeout value is correctly passed through to request options"""

    # GIVEN a workflow with timeout in settings
    workflow = BasicInlinePromptWorkflow()

    # AND a simple mock response
    def generate_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        yield InitiatedExecutePromptEvent(execution_id=execution_id)

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_events

    # WHEN we run the workflow
    workflow.run(inputs=WorkflowInputs(noun="color"))

    # THEN verify the timeout was passed correctly in request_options
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.assert_called_once()
    call_kwargs = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args.kwargs
    assert call_kwargs["request_options"]["timeout_in_seconds"] == 1  # Matches our PromptSettings(timeout=1)
