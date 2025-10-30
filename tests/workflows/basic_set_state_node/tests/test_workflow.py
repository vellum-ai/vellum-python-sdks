from uuid import uuid4
from typing import Iterator, List

from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.string_vellum_value import StringVellumValue

from tests.workflows.basic_set_state_node.workflow import BasicSetStateNodeWorkflow, Inputs


def test_run_workflow__happy_path(vellum_adhoc_prompt_client):
    """
    Test that the SetStateNode can concatenate chat history from an agent node.
    """

    def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())

        expected_outputs: List[PromptOutput] = [
            StringVellumValue(value="Hello! How can I help you today?"),
        ]

        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # GIVEN a workflow that uses SetStateNode with agent concatenation
    workflow = BasicSetStateNodeWorkflow()

    # WHEN we run the workflow with an initial message
    terminal_event = workflow.run(inputs=Inputs(message="Hello!"))

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the state should be updated with chat history
    assert terminal_event.outputs.chat_history == [
        ChatMessage(text="Hello! How can I help you today?", role="ASSISTANT", content=None)
    ]
    assert terminal_event.outputs.counter == 1
