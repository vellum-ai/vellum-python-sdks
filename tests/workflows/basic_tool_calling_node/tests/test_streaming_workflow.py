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
            first_events: List[ExecutePromptEvent] = [
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
            second_events: List[ExecutePromptEvent] = [
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
        if call_count == 1:
            yield from first_events
        else:
            yield from second_events

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
    assert streaming_event_1.output.delta is not None
    delta_1 = streaming_event_1.output.delta
    assert isinstance(delta_1, list)
    assert len(delta_1) == 1
    assert delta_1[0].role == "ASSISTANT"
    assert delta_1[0].content.type == "FUNCTION_CALL"
    assert delta_1[0].content.value.name == "get_current_weather"
    assert delta_1[0].content.value.arguments == {"location": "San Francisco", "unit": "celsius"}
    assert delta_1[0].content.value.id == "call_7115tNTmEACTsQRGwKpJipJK"
    assert delta_1[0].content.value.state == "FULFILLED"

    streaming_event_2 = chat_history_events[2]
    assert streaming_event_2.output.is_streaming
    assert streaming_event_2.output.delta is not None
    delta_2 = streaming_event_2.output.delta
    assert isinstance(delta_2, list)
    assert len(delta_2) == 1
    assert delta_2[0].role == "FUNCTION"
    assert delta_2[0].content.type == "STRING"
    assert (
        delta_2[0].content.value
        == '"The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."'
    )

    streaming_event_3 = chat_history_events[3]
    assert streaming_event_3.output.is_streaming
    assert streaming_event_3.output.delta is not None
    delta_3 = streaming_event_3.output.delta
    assert isinstance(delta_3, list)
    assert len(delta_3) == 1
    assert (
        delta_3[0].text == "Based on the function call, the current temperature in San Francisco is 70 degrees celsius."
    )
    assert delta_3[0].role == "ASSISTANT"

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
            first_events: List[ExecutePromptEvent] = [
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
            second_events: List[ExecutePromptEvent] = [
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

        if call_count == 1:
            yield from first_events
        else:
            yield from second_events

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

    first_chat_deltas = []

    assert first_chat_streaming_events[0].output.is_streaming
    assert first_chat_streaming_events[0].output.name == "chat_history"
    assert first_chat_streaming_events[0].output.delta is not None
    delta_0 = first_chat_streaming_events[0].output.delta
    assert isinstance(delta_0, list)
    assert delta_0[0].text == "Let"
    first_chat_deltas.append(delta_0[0].text)

    assert first_chat_streaming_events[1].output.is_streaming
    assert first_chat_streaming_events[1].output.name == "chat_history"
    assert first_chat_streaming_events[1].output.delta is not None
    delta_1 = first_chat_streaming_events[1].output.delta
    assert isinstance(delta_1, list)
    assert delta_1[0].text == " me"
    first_chat_deltas.append(delta_1[0].text)

    assert first_chat_streaming_events[2].output.is_streaming
    assert first_chat_streaming_events[2].output.name == "chat_history"
    assert first_chat_streaming_events[2].output.delta is not None
    delta_2 = first_chat_streaming_events[2].output.delta
    assert isinstance(delta_2, list)
    assert delta_2[0].text == " check"
    first_chat_deltas.append(delta_2[0].text)

    assert first_chat_streaming_events[3].output.is_streaming
    assert first_chat_streaming_events[3].output.name == "chat_history"
    assert first_chat_streaming_events[3].output.delta is not None
    delta_3 = first_chat_streaming_events[3].output.delta
    assert isinstance(delta_3, list)
    assert delta_3[0].text == " the"
    first_chat_deltas.append(delta_3[0].text)

    assert first_chat_streaming_events[4].output.is_streaming
    assert first_chat_streaming_events[4].output.name == "chat_history"
    assert first_chat_streaming_events[4].output.delta is not None
    delta_4 = first_chat_streaming_events[4].output.delta
    assert isinstance(delta_4, list)
    assert delta_4[0].text == " weather."
    first_chat_deltas.append(delta_4[0].text)
    first_combined_chat_text = "".join(first_chat_deltas)
    assert first_combined_chat_text == expected_first_chat_message

    assert function_result_event.output.name == "chat_history"
    assert function_result_event.output.delta is not None
    func_delta = function_result_event.output.delta
    assert isinstance(func_delta, list)
    assert len(func_delta) == 1
    function_message = func_delta[0]
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

    second_chat_deltas = []

    assert second_chat_streaming_events[0].output.is_streaming
    assert second_chat_streaming_events[0].output.name == "chat_history"
    assert second_chat_streaming_events[0].output.delta is not None
    second_delta_0 = second_chat_streaming_events[0].output.delta
    assert isinstance(second_delta_0, list)
    assert second_delta_0[0].text == "Based"
    second_chat_deltas.append(second_delta_0[0].text)

    assert second_chat_streaming_events[1].output.is_streaming
    assert second_chat_streaming_events[1].output.name == "chat_history"
    assert second_chat_streaming_events[1].output.delta is not None
    second_delta_1 = second_chat_streaming_events[1].output.delta
    assert isinstance(second_delta_1, list)
    assert second_delta_1[0].text == " on"
    second_chat_deltas.append(second_delta_1[0].text)

    assert second_chat_streaming_events[2].output.is_streaming
    assert second_chat_streaming_events[2].output.name == "chat_history"
    assert second_chat_streaming_events[2].output.delta is not None
    second_delta_2 = second_chat_streaming_events[2].output.delta
    assert isinstance(second_delta_2, list)
    assert second_delta_2[0].text == " the"
    second_chat_deltas.append(second_delta_2[0].text)

    assert second_chat_streaming_events[3].output.is_streaming
    assert second_chat_streaming_events[3].output.name == "chat_history"
    assert second_chat_streaming_events[3].output.delta is not None
    second_delta_3 = second_chat_streaming_events[3].output.delta
    assert isinstance(second_delta_3, list)
    assert second_delta_3[0].text == " function"
    second_chat_deltas.append(second_delta_3[0].text)

    assert second_chat_streaming_events[4].output.is_streaming
    assert second_chat_streaming_events[4].output.name == "chat_history"
    assert second_chat_streaming_events[4].output.delta is not None
    second_delta_4 = second_chat_streaming_events[4].output.delta
    assert isinstance(second_delta_4, list)
    assert second_delta_4[0].text == " call,"
    second_chat_deltas.append(second_delta_4[0].text)

    assert second_chat_streaming_events[5].output.is_streaming
    assert second_chat_streaming_events[5].output.name == "chat_history"
    assert second_chat_streaming_events[5].output.delta is not None
    second_delta_5 = second_chat_streaming_events[5].output.delta
    assert isinstance(second_delta_5, list)
    assert second_delta_5[0].text == " the"
    second_chat_deltas.append(second_delta_5[0].text)

    assert second_chat_streaming_events[6].output.is_streaming
    assert second_chat_streaming_events[6].output.name == "chat_history"
    assert second_chat_streaming_events[6].output.delta is not None
    second_delta_6 = second_chat_streaming_events[6].output.delta
    assert isinstance(second_delta_6, list)
    assert second_delta_6[0].text == " current"
    second_chat_deltas.append(second_delta_6[0].text)

    assert second_chat_streaming_events[7].output.is_streaming
    assert second_chat_streaming_events[7].output.name == "chat_history"
    assert second_chat_streaming_events[7].output.delta is not None
    second_delta_7 = second_chat_streaming_events[7].output.delta
    assert isinstance(second_delta_7, list)
    assert second_delta_7[0].text == " temperature"
    second_chat_deltas.append(second_delta_7[0].text)

    assert second_chat_streaming_events[8].output.is_streaming
    assert second_chat_streaming_events[8].output.name == "chat_history"
    assert second_chat_streaming_events[8].output.delta is not None
    second_delta_8 = second_chat_streaming_events[8].output.delta
    assert isinstance(second_delta_8, list)
    assert second_delta_8[0].text == " in"
    second_chat_deltas.append(second_delta_8[0].text)

    assert second_chat_streaming_events[9].output.is_streaming
    assert second_chat_streaming_events[9].output.name == "chat_history"
    assert second_chat_streaming_events[9].output.delta is not None
    second_delta_9 = second_chat_streaming_events[9].output.delta
    assert isinstance(second_delta_9, list)
    assert second_delta_9[0].text == " San"
    second_chat_deltas.append(second_delta_9[0].text)

    assert second_chat_streaming_events[10].output.is_streaming
    assert second_chat_streaming_events[10].output.name == "chat_history"
    assert second_chat_streaming_events[10].output.delta is not None
    second_delta_10 = second_chat_streaming_events[10].output.delta
    assert isinstance(second_delta_10, list)
    assert second_delta_10[0].text == " Francisco"
    second_chat_deltas.append(second_delta_10[0].text)

    assert second_chat_streaming_events[11].output.is_streaming
    assert second_chat_streaming_events[11].output.name == "chat_history"
    assert second_chat_streaming_events[11].output.delta is not None
    second_delta_11 = second_chat_streaming_events[11].output.delta
    assert isinstance(second_delta_11, list)
    assert second_delta_11[0].text == " is"
    second_chat_deltas.append(second_delta_11[0].text)

    assert second_chat_streaming_events[12].output.is_streaming
    assert second_chat_streaming_events[12].output.name == "chat_history"
    assert second_chat_streaming_events[12].output.delta is not None
    second_delta_12 = second_chat_streaming_events[12].output.delta
    assert isinstance(second_delta_12, list)
    assert second_delta_12[0].text == " 70"
    second_chat_deltas.append(second_delta_12[0].text)

    assert second_chat_streaming_events[13].output.is_streaming
    assert second_chat_streaming_events[13].output.name == "chat_history"
    assert second_chat_streaming_events[13].output.delta is not None
    second_delta_13 = second_chat_streaming_events[13].output.delta
    assert isinstance(second_delta_13, list)
    assert second_delta_13[0].text == " degrees"
    second_chat_deltas.append(second_delta_13[0].text)

    assert second_chat_streaming_events[14].output.is_streaming
    assert second_chat_streaming_events[14].output.name == "chat_history"
    assert second_chat_streaming_events[14].output.delta is not None
    second_delta_14 = second_chat_streaming_events[14].output.delta
    assert isinstance(second_delta_14, list)
    assert second_delta_14[0].text == " celsius."
    second_chat_deltas.append(second_delta_14[0].text)

    all_chat_deltas = first_chat_deltas + second_chat_deltas
    all_combined_chat_text = "".join(all_chat_deltas)

    expected_combined_text = expected_first_chat_message + expected_second_chat_message
    assert all_combined_chat_text == expected_combined_text

    final_event = events[-1]
    assert final_event.name == "workflow.execution.fulfilled"
    final_chat_history = final_event.body.outputs.chat_history
    assert len(final_chat_history) == 3
    assert final_chat_history[2].text == expected_second_chat_message
