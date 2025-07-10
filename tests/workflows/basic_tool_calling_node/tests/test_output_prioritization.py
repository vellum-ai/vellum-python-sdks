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


def test_output_prioritization_during_streaming(vellum_adhoc_prompt_client):
    """
    Test that chat_history is prioritized during streaming state.
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
                        id="call_test",
                        name="get_current_weather",
                        state="FULFILLED",
                    ),
                ),
            ]
        else:
            expected_outputs = [StringVellumValue(value="The weather is 70 degrees celsius.")]

        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(execution_id=execution_id, outputs=expected_outputs),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events
    workflow = BasicToolCallingNodeWorkflow()

    result = workflow.stream(inputs=Inputs(query="What's the weather like in San Francisco?"))
    events = list(result)

    streaming_events = [e for e in events if e.name == "workflow.execution.streaming"]

    output_order = []
    for event in streaming_events:
        if event.output.name in ["chat_history", "text"]:
            if event.output.is_streaming:
                output_order.append(f"{event.output.name}_streaming")
            elif event.output.is_fulfilled:
                output_order.append(f"{event.output.name}_fulfilled")

    streaming_outputs = [o for o in output_order if "_streaming" in o]
    if streaming_outputs:
        assert streaming_outputs[0].startswith(
            "chat_history"
        ), f"Expected chat_history first during streaming, got: {output_order}"

    fulfilled_outputs = [o for o in output_order if "_fulfilled" in o]
    if len(fulfilled_outputs) >= 2:
        text_fulfilled_idx = next((i for i, o in enumerate(output_order) if o == "text_fulfilled"), -1)
        chat_history_fulfilled_idx = next((i for i, o in enumerate(output_order) if o == "chat_history_fulfilled"), -1)

        if text_fulfilled_idx != -1 and chat_history_fulfilled_idx != -1:
            assert (
                text_fulfilled_idx < chat_history_fulfilled_idx
            ), f"Expected text_fulfilled before chat_history_fulfilled, got order: {output_order}"


def test_output_prioritization_when_fulfilled(vellum_adhoc_prompt_client):
    """
    Test that text is prioritized when both outputs are fulfilled.
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
                        id="call_test",
                        name="get_current_weather",
                        state="FULFILLED",
                    ),
                ),
            ]
        else:
            expected_outputs = [StringVellumValue(value="The weather is 70 degrees celsius.")]

        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(execution_id=execution_id, outputs=expected_outputs),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events
    workflow = BasicToolCallingNodeWorkflow()

    result = workflow.stream(inputs=Inputs(query="What's the weather?"))
    events = list(result)

    fulfilled_events = [e for e in events if e.name == "workflow.execution.fulfilled"]
    assert len(fulfilled_events) == 1

    fulfilled_event = fulfilled_events[0]
    output_names = [output[0].name for output in fulfilled_event.outputs]

    if "text" in output_names and "chat_history" in output_names:
        text_idx = output_names.index("text")
        chat_history_idx = output_names.index("chat_history")
        assert (
            text_idx < chat_history_idx
        ), f"Expected text before chat_history in fulfilled outputs, got: {output_names}"
