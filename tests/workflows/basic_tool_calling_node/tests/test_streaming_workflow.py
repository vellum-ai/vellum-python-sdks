from uuid import uuid4
from typing import Iterator, List

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.streaming_execute_prompt_event import StreamingExecutePromptEvent
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
        events: List[ExecutePromptEvent]
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
            events = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                FulfilledExecutePromptEvent(
                    execution_id=execution_id,
                    outputs=expected_outputs,
                ),
            ]
        else:
            events = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                StreamingExecutePromptEvent(
                    execution_id=execution_id,
                    output=StringVellumValue(value="Based on the function call, "),
                    output_index=0,
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id,
                    output=StringVellumValue(value="the current temperature in San Francisco "),
                    output_index=0,
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id,
                    output=StringVellumValue(value="is 70 degrees celsius."),
                    output_index=0,
                ),
                FulfilledExecutePromptEvent(
                    execution_id=execution_id,
                    outputs=[
                        StringVellumValue(
                            value="Based on the function call, the current temperature in San Francisco is 70 degrees celsius."  # noqa: E501
                        )
                    ],
                ),
            ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    workflow = BasicToolCallingNodeWorkflow()

    result = workflow.stream(inputs=Inputs(query="What's the weather like in San Francisco?"))
    events = list(result)

    streaming_events = [e for e in events if e.name == "workflow.execution.streaming"]
    chat_history_events = [e for e in streaming_events if e.output.name == "chat_history"]

    first_event = chat_history_events[0]
    assert first_event.output.is_initiated

    text_streaming_events = [
        event
        for event in chat_history_events[1:-1]  # Skip initiated and fulfilled
        if (
            event.output.is_streaming
            and isinstance(event.output.delta, list)
            and len(event.output.delta) == 1
            and event.output.delta[0].text is not None
            and event.output.delta[0].role == "ASSISTANT"
        )
    ]

    assert len(text_streaming_events) == 3

    # Verify the exact text content matches our mocked deltas
    assert isinstance(text_streaming_events[0].output.delta, list)
    assert text_streaming_events[0].output.delta[0].text == "Based on the function call, "
    assert text_streaming_events[0].output.delta[0].role == "ASSISTANT"

    assert isinstance(text_streaming_events[1].output.delta, list)
    assert text_streaming_events[1].output.delta[0].text == "the current temperature in San Francisco "
    assert text_streaming_events[1].output.delta[0].role == "ASSISTANT"

    assert isinstance(text_streaming_events[2].output.delta, list)
    assert text_streaming_events[2].output.delta[0].text == "is 70 degrees celsius."
    assert text_streaming_events[2].output.delta[0].role == "ASSISTANT"

    final_event = chat_history_events[-1]
    assert final_event.output.is_fulfilled
    final_chat_history = final_event.output.value
    assert len(final_chat_history) == 3
