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

        if call_count == 1:
            # First call: Stream function call
            events: List[ExecutePromptEvent] = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                StreamingExecutePromptEvent(
                    execution_id=execution_id,
                    output=FunctionCallVellumValue(
                        value=FunctionCall(
                            arguments={"location": "San Francisco", "unit": "celsius"},
                            id="call_7115tNTmEACTsQRGwKpJipJK",
                            name="get_current_weather",
                            state="FULFILLED",
                        ),
                    ),
                    output_index=0,
                ),
                FulfilledExecutePromptEvent(
                    execution_id=execution_id,
                    outputs=expected_outputs,
                ),
            ]
        else:
            # Second call: Stream final response
            events: List[ExecutePromptEvent] = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                StreamingExecutePromptEvent(
                    execution_id=execution_id,
                    output=StringVellumValue(
                        value="Based on the function call, the current temperature in San Francisco is 70 degrees celsius."  # noqa: E501
                    ),
                    output_index=0,
                ),
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

    first_event = chat_history_events[0]
    assert first_event.output.is_initiated

    streaming_event_1 = chat_history_events[1]
    assert streaming_event_1.output.is_streaming
    assert len(streaming_event_1.output.delta) == 1
    assert streaming_event_1.output.delta[0].role == "ASSISTANT"
    assert streaming_event_1.output.delta[0].content.type == "FUNCTION_CALL"
    assert streaming_event_1.output.delta[0].content.value.name == "get_current_weather"
    assert streaming_event_1.output.delta[0].content.value.arguments == {"location": "San Francisco", "unit": "celsius"}
    assert streaming_event_1.output.delta[0].content.value.id == "call_7115tNTmEACTsQRGwKpJipJK"
    assert streaming_event_1.output.delta[0].content.value.state == "FULFILLED"

    streaming_event_2 = chat_history_events[2]
    assert streaming_event_2.output.is_streaming
    assert len(streaming_event_2.output.delta) == 1
    assert streaming_event_2.output.delta[0].role == "FUNCTION"
    assert streaming_event_2.output.delta[0].content.type == "STRING"
    assert (
        streaming_event_2.output.delta[0].content.value
        == '"The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."'
    )

    streaming_event_3 = chat_history_events[3]
    assert streaming_event_3.output.is_streaming
    assert len(streaming_event_3.output.delta) == 1
    assert (
        streaming_event_3.output.delta[0].text
        == "Based on the function call, the current temperature in San Francisco is 70 degrees celsius."
    )
    assert streaming_event_3.output.delta[0].role == "ASSISTANT"

    fulfilled_event = chat_history_events[4]
    assert fulfilled_event.output.is_fulfilled
    assert len(fulfilled_event.output.value) == 3

    assert len(chat_history_events) == 5


def test_stream_chat_history_content__deltas_equal_final_value(vellum_adhoc_prompt_client):
    expected_first_chat_message = "Let me check the weather."
    expected_second_chat_message = (
        "Based on the function call, the current temperature in San Francisco is 70 degrees celsius."
    )

    def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())

        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count

        if call_count == 1:
            events: List[ExecutePromptEvent] = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value="Let"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" me"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" check"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" the"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" weather."), output_index=0
                ),
                FulfilledExecutePromptEvent(
                    execution_id=execution_id,
                    outputs=[
                        FunctionCallVellumValue(
                            value=FunctionCall(
                                arguments={"location": "San Francisco", "unit": "celsius"},
                                id="call_7115tNTmEACTsQRGwKpJipJK",
                                name="get_current_weather",
                                state="FULFILLED",
                            ),
                        ),
                    ],
                ),
            ]
        else:
            events: List[ExecutePromptEvent] = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value="Based"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" on"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" the"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" function"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" call,"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" the"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" current"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" temperature"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" in"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" San"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" Francisco"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" is"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" 70"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" degrees"), output_index=0
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id, output=StringVellumValue(value=" celsius."), output_index=0
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

    all_chat_history_events = [
        e for e in events if e.name == "workflow.execution.streaming" and e.output.name == "chat_history"
    ]

    first_chat_history_events = all_chat_history_events[:6]  # initiated + 5 deltas
    function_result_event = all_chat_history_events[6]  # function result delta
    second_chat_history_events = all_chat_history_events[7:]  # remaining deltas + fulfilled

    first_chat_streaming_events = [e for e in first_chat_history_events if e.output.is_streaming]
    assert len(first_chat_streaming_events) == 5

    assert first_chat_streaming_events[0].output.is_streaming
    assert first_chat_streaming_events[0].output.name == "chat_history"
    assert first_chat_streaming_events[0].output.delta[0].text == "Let"

    assert first_chat_streaming_events[1].output.is_streaming
    assert first_chat_streaming_events[1].output.name == "chat_history"
    assert first_chat_streaming_events[1].output.delta[0].text == " me"

    assert first_chat_streaming_events[2].output.is_streaming
    assert first_chat_streaming_events[2].output.name == "chat_history"
    assert first_chat_streaming_events[2].output.delta[0].text == " check"

    assert first_chat_streaming_events[3].output.is_streaming
    assert first_chat_streaming_events[3].output.name == "chat_history"
    assert first_chat_streaming_events[3].output.delta[0].text == " the"

    assert first_chat_streaming_events[4].output.is_streaming
    assert first_chat_streaming_events[4].output.name == "chat_history"
    assert first_chat_streaming_events[4].output.delta[0].text == " weather."

    first_chat_deltas = [event.output.delta[0].text for event in first_chat_streaming_events]
    first_combined_chat_text = "".join(first_chat_deltas)
    assert first_combined_chat_text == expected_first_chat_message

    assert function_result_event.output.name == "chat_history"
    assert isinstance(function_result_event.output.delta, list)
    assert len(function_result_event.output.delta) == 1
    function_message = function_result_event.output.delta[0]
    assert function_message.role == "FUNCTION"
    assert function_message.source == "call_7115tNTmEACTsQRGwKpJipJK"

    final_chat_events = [
        e
        for e in events
        if e.name == "workflow.execution.streaming" and e.output.name == "chat_history" and e.output.is_fulfilled
    ]
    final_chat_event = final_chat_events[-1]
    assert len(final_chat_event.output.value) == 3  # Assistant + Function + Assistant

    second_chat_streaming_events = [e for e in second_chat_history_events if e.output.is_streaming]
    assert len(second_chat_streaming_events) == 15

    assert second_chat_streaming_events[0].output.is_streaming
    assert second_chat_streaming_events[0].output.name == "chat_history"
    assert second_chat_streaming_events[0].output.delta[0].text == "Based"

    assert second_chat_streaming_events[1].output.is_streaming
    assert second_chat_streaming_events[1].output.name == "chat_history"
    assert second_chat_streaming_events[1].output.delta[0].text == " on"

    assert second_chat_streaming_events[2].output.is_streaming
    assert second_chat_streaming_events[2].output.name == "chat_history"
    assert second_chat_streaming_events[2].output.delta[0].text == " the"

    assert second_chat_streaming_events[3].output.is_streaming
    assert second_chat_streaming_events[3].output.name == "chat_history"
    assert second_chat_streaming_events[3].output.delta[0].text == " function"

    assert second_chat_streaming_events[4].output.is_streaming
    assert second_chat_streaming_events[4].output.name == "chat_history"
    assert second_chat_streaming_events[4].output.delta[0].text == " call,"

    second_chat_deltas = [event.output.delta[0].text for event in second_chat_streaming_events]
    second_combined_chat_text = "".join(second_chat_deltas)
    assert second_combined_chat_text == expected_second_chat_message

    all_chat_streaming_events = first_chat_streaming_events + second_chat_streaming_events
    all_chat_deltas = [event.output.delta[0].text for event in all_chat_streaming_events]
    all_combined_chat_text = "".join(all_chat_deltas)

    expected_combined_text = expected_first_chat_message + expected_second_chat_message
    assert all_combined_chat_text == expected_combined_text

    final_event = events[-1]
    assert final_event.name == "workflow.execution.fulfilled"
    final_chat_history = final_event.body.outputs.chat_history
    assert len(final_chat_history) == 3
    assert final_chat_history[2].text == expected_second_chat_message
