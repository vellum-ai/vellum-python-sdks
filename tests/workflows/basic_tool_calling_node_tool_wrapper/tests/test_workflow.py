from uuid import uuid4
from typing import Iterator, List

from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_chat_message_content import FunctionCallChatMessageContent
from vellum.client.types.function_call_chat_message_content_value import FunctionCallChatMessageContentValue
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.function_definition import FunctionDefinition
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.string_chat_message_content import StringChatMessageContent
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.workflows.events.workflow import WorkflowExecutionFulfilledEvent

from tests.workflows.basic_tool_calling_node_tool_wrapper.workflow import BasicToolCallingNodeWrapperWorkflow, Inputs


def test_wrapper_workflow_sends_examples_and_merges_inputs(vellum_adhoc_prompt_client):
    def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())

        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
        expected_outputs: List[PromptOutput]
        if call_count == 1:
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"location": "San Francisco", "units": "celsius"},
                        id="call_weather",
                        name="get_current_weather",
                        state="FULFILLED",
                    ),
                ),
            ]
        else:
            expected_outputs = [
                StringVellumValue(
                    value="The current weather on 2024-01-01 in San Francisco is sunny with a temperature of 70 degrees celsius.",  # noqa: E501
                )
            ]

        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(execution_id=execution_id, outputs=expected_outputs),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    workflow = BasicToolCallingNodeWrapperWorkflow()

    terminal_event = workflow.run(Inputs(date_input="2024-01-01"))
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert isinstance(terminal_event, WorkflowExecutionFulfilledEvent)

    assert terminal_event.outputs.text == (
        "The current weather on 2024-01-01 in San Francisco is sunny with a temperature of 70 degrees celsius."
    )

    first_call = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0]
    functions = first_call.kwargs["functions"]
    assert functions == [
        FunctionDefinition(
            state=None,
            cache_config=None,
            name="get_current_weather",
            description=None,
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to get the weather for",
                    },
                    "units": {
                        "type": "string",
                        "description": "The unit of temperature",
                        "default": "fahrenheit",
                    },
                },
                "required": ["location"],
                "examples": [
                    {"location": "San Francisco"},
                    {"location": "New York", "units": "celsius"},
                ],
            },
            inputs=None,
            forced=None,
            strict=None,
        )
    ]

    chat_history = terminal_event.outputs.chat_history
    assert chat_history == [
        ChatMessage(
            text=None,
            role="ASSISTANT",
            content=FunctionCallChatMessageContent(
                type="FUNCTION_CALL",
                value=FunctionCallChatMessageContentValue(
                    name="get_current_weather",
                    arguments={"location": "San Francisco", "units": "celsius"},
                    id="call_weather",
                ),
            ),
            source=None,
        ),
        ChatMessage(
            text=None,
            role="FUNCTION",
            content=StringChatMessageContent(
                type="STRING",
                value='"The current weather on 2024-01-01 in San Francisco is sunny with a temperature of 70 degrees celsius."',  # noqa: E501
            ),
            source="call_weather",
        ),
        ChatMessage(
            text="The current weather on 2024-01-01 in San Francisco is sunny with a temperature of 70 degrees celsius.",  # noqa: E501
            role="ASSISTANT",
            content=None,
            source=None,
        ),
    ]
