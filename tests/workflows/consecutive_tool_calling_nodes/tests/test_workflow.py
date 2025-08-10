from uuid import uuid4
from typing import Iterator, List

from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.string_vellum_value import StringVellumValue

from tests.workflows.consecutive_tool_calling_nodes.workflow import ConsecutiveToolCallingNodesWorkflow


def test_consecutive_tool_calling_nodes__should_call_both_nodes(vellum_adhoc_prompt_client, mock_uuid4_generator):
    """
    Test that consecutive ToolCallingNodes with no tools both execute.
    This test should fail on main branch, demonstrating the reported bug.
    """

    call_count = 0

    def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
        nonlocal call_count
        call_count += 1
        execution_id = str(uuid4())

        if call_count == 1:
            expected_outputs = [StringVellumValue(value="First node response")]
        else:
            expected_outputs = [StringVellumValue(value="Second node response")]

        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    # Set up the mock to return our events
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    mock_uuid4_generator("vellum.workflows.nodes.displayable.bases.inline_prompt_node.node.uuid4")

    workflow = ConsecutiveToolCallingNodesWorkflow()

    # WHEN the workflow is executed
    terminal_event = workflow.run()

    assert terminal_event.name == "workflow.execution.fulfilled"

    assert vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count == 2

    assert terminal_event.outputs.text == "Second node response"
    assert terminal_event.outputs.chat_history == [
        ChatMessage(
            text="Second node response",
            role="ASSISTANT",
            content=None,
            source=None,
        )
    ]
