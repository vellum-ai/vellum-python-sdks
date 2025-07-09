from uuid import uuid4
from typing import Iterator, List

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.string_vellum_value import StringVellumValue

from tests.workflows.basic_tool_calling_node.workflow import BasicToolCallingNodeWorkflow, Inputs


def test_stream_workflow__happy_path(vellum_adhoc_prompt_client):
    """
    Test that ToolCallingNode streams chat_history updates as they become available.
    """

    def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())

        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
        expected_outputs: List[PromptOutput]
        if call_count == 1:
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"location": "San Francisco", "unit": "celsius"},
                        id="call_7115tNTmEACTsQRGwKpJipJK",
                        name="get_current_weather",
                        state="FULFILLED",
                    ),
                ),
            ]
        else:
            expected_outputs = [
                StringVellumValue(
                    value="Based on the function call, the current temperature in San Francisco is 70 degrees celsius."
                )
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

    workflow = BasicToolCallingNodeWorkflow()

    result = workflow.stream(inputs=Inputs(query="What's the weather like in San Francisco?"))
    events = list(result)

    streaming_events = [e for e in events if e.name == "workflow.execution.streaming"]
    chat_history_events = [e for e in streaming_events if e.output.name == "chat_history"]

    assert len(chat_history_events) >= 1

    final_chat_event = chat_history_events[-1]
    assert final_chat_event.output.is_fulfilled
    final_chat_history = final_chat_event.output.value
    assert len(final_chat_history) == 3

    assert final_chat_history[0].role == "ASSISTANT"
    assert final_chat_history[0].content.type == "FUNCTION_CALL"
    assert final_chat_history[0].content.value.name == "get_current_weather"

    assert final_chat_history[1].role == "FUNCTION"
    assert final_chat_history[1].content.type == "STRING"

    assert final_chat_history[2].role == "ASSISTANT"
    assert (
        final_chat_history[2].text
        == "Based on the function call, the current temperature in San Francisco is 70 degrees celsius."
    )

    final_workflow_event = [e for e in events if e.name == "workflow.execution.fulfilled"][0]
    assert final_workflow_event.outputs.chat_history == final_chat_history
