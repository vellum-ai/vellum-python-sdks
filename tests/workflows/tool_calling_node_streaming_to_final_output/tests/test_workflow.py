from uuid import uuid4
from typing import Any, Iterator, List

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.streaming_execute_prompt_event import StreamingExecutePromptEvent
from vellum.client.types.string_vellum_value import StringVellumValue

from tests.workflows.tool_calling_node_streaming_to_final_output.workflow import (
    Inputs,
    ToolCallingNodeStreamingToFinalOutputWorkflow,
)


def test_workflow__happy_path(vellum_adhoc_prompt_client):
    """
    Test that ToolCallingNode streams text chunks through FinalOutputNode to workflow output.
    """
    # GIVEN a workflow with a ToolCallingNode and a FinalOutputNode
    workflow = ToolCallingNodeStreamingToFinalOutputWorkflow()

    call_count = 0

    def generate_prompt_events(*_args: Any, **_kwargs: Any) -> Iterator[ExecutePromptEvent]:
        nonlocal call_count
        call_count += 1
        execution_id = str(uuid4())

        if call_count == 1:
            # First call: function call
            expected_outputs_1: List[PromptOutput] = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"location": "San Francisco", "unit": "celsius"},
                        id="call_7115tNTmEACTsQRGwKpJipJK",
                        name="get_current_weather",
                        state="FULFILLED",
                    ),
                ),
            ]
            events: List[ExecutePromptEvent] = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                FulfilledExecutePromptEvent(
                    execution_id=execution_id,
                    outputs=expected_outputs_1,
                ),
            ]
        else:
            # Second call: text response (streaming chunks)
            expected_outputs_2: List[PromptOutput] = [
                StringVellumValue(
                    value="The weather in San Francisco is sunny with a temperature of 70 degrees celsius."
                ),
            ]
            events = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                StreamingExecutePromptEvent(
                    execution_id=execution_id,
                    output=StringVellumValue(value="The weather"),
                    output_index=0,
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id,
                    output=StringVellumValue(value=" in San Francisco"),
                    output_index=0,
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id,
                    output=StringVellumValue(value=" is sunny with a temperature of 70 degrees celsius."),
                    output_index=0,
                ),
                FulfilledExecutePromptEvent(
                    execution_id=execution_id,
                    outputs=expected_outputs_2,
                ),
            ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN the workflow is streamed
    stream = workflow.stream(inputs=Inputs(query="What's the weather like in San Francisco?"))
    events = list(stream)

    # THEN there should be workflow.execution.streaming events emitted for each chunk
    # + 2 more for initiated and fulfilled outputs
    streaming_events = [event for event in events if event.name == "workflow.execution.streaming"]
    assert len(streaming_events) == 5

    final_output_streaming_events = [event for event in streaming_events if event.output.name == "final_output"]

    initiated_events = [e for e in final_output_streaming_events if e.output.is_initiated]
    streaming_events_list = [e for e in final_output_streaming_events if e.output.is_streaming]
    fulfilled_events = [e for e in final_output_streaming_events if e.output.is_fulfilled]

    assert len(initiated_events) == 1
    assert len(streaming_events_list) == 3
    assert len(fulfilled_events) == 1

    assert streaming_events_list[0].output.delta == "The weather"
    assert streaming_events_list[1].output.delta == " in San Francisco"
    assert streaming_events_list[2].output.delta == " is sunny with a temperature of 70 degrees celsius."

    assert (
        fulfilled_events[-1].output.value
        == "The weather in San Francisco is sunny with a temperature of 70 degrees celsius."
    )
