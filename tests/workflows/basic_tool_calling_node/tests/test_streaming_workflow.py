from uuid import uuid4
from typing import Iterator, List, Any

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
                FulfilledExecutePromptEvent(
                    execution_id=execution_id,
                    outputs=expected_outputs,
                ),
            ]
        else:
            expected_outputs = [
                StringVellumValue(
                    value="Based on the function call, the current temperature in San Francisco is 70 degrees celsius."
                )
            ]
            second_events: List[ExecutePromptEvent] = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
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

    event_0 = chat_history_events[0]
    assert event_0.output.is_initiated
    assert event_0.output.name == "chat_history"

    event_1 = chat_history_events[1]
    assert event_1.output.is_streaming
    assert len(event_1.output.delta) == 1
    assert isinstance(event_1.output.delta, list)
    assert event_1.output.delta[0].role == "ASSISTANT"
    assert event_1.output.delta[0].text == "Let"

    event_2 = chat_history_events[2]
    assert event_2.output.is_streaming
    assert len(event_2.output.delta) == 1
    assert isinstance(event_2.output.delta, list)
    assert event_2.output.delta[0].text == " me"

    event_3 = chat_history_events[3]
    assert event_3.output.is_streaming
    assert len(event_3.output.delta) == 1
    assert isinstance(event_3.output.delta, list)
    assert event_3.output.delta[0].text == " check"

    event_4 = chat_history_events[4]
    assert event_4.output.is_streaming
    assert len(event_4.output.delta) == 1
    assert isinstance(event_4.output.delta, list)
    assert event_4.output.delta[0].role == "ASSISTANT"
    assert event_4.output.delta[0].content.type == "FUNCTION_CALL"
    assert event_4.output.delta[0].content.value.name == "get_current_weather"

    event_5 = chat_history_events[5]
    assert event_5.output.is_streaming
    assert len(event_5.output.delta) == 2  # Function call + function result
    assert isinstance(event_5.output.delta, list)
    assert event_5.output.delta[0].role == "ASSISTANT"
    assert event_5.output.delta[0].content.type == "FUNCTION_CALL"
    assert event_5.output.delta[1].role == "FUNCTION"
    assert event_5.output.delta[1].content.type == "STRING"

    event_6 = chat_history_events[6]
    assert event_6.output.is_streaming
    assert len(event_6.output.delta) == 3  # All messages: function call + function result + final response
    assert isinstance(event_6.output.delta, list)
    assert event_6.output.delta[2].role == "ASSISTANT"
    assert (
        event_6.output.delta[2].text
        == "Based on the function call, the current temperature in San Francisco is 70 degrees celsius."
    )

    event_7 = chat_history_events[7]
    assert event_7.output.is_fulfilled
    final_chat_history = event_7.output.value
    assert len(final_chat_history) == 3

    assert len(chat_history_events) == 8
