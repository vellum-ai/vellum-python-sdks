import pytest
from unittest import mock
from uuid import uuid4
from typing import Iterator, List

from vellum.client.types.ad_hoc_expand_meta import AdHocExpandMeta
from vellum.client.types.array_chat_message_content import ArrayChatMessageContent
from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_chat_message_content import FunctionCallChatMessageContent
from vellum.client.types.function_call_chat_message_content_value import FunctionCallChatMessageContentValue
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.function_definition import FunctionDefinition
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.prompt_parameters import PromptParameters
from vellum.client.types.prompt_request_chat_history_input import PromptRequestChatHistoryInput
from vellum.client.types.prompt_request_json_input import PromptRequestJsonInput
from vellum.client.types.prompt_request_string_input import PromptRequestStringInput
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.string_chat_message_content import StringChatMessageContent
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.client.types.vellum_variable import VellumVariable
from vellum.workflows.events.node import NodeExecutionInitiatedEvent
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.nodes.displayable.tool_calling_node.utils import ToolPromptNode
from vellum.workflows.workflows.base import BaseWorkflow
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.basic_tool_calling_node.workflow import BasicToolCallingNodeWorkflow, Inputs


def test_run_workflow__happy_path(vellum_adhoc_prompt_client, vellum_client, mock_uuid4_generator):
    """
    Test that the GetCurrentWeatherWorkflow returns the expected outputs.
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

    # Set up the mock to return our events
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    uuid4_generator = mock_uuid4_generator("vellum.workflows.nodes.displayable.bases.inline_prompt_node.node.uuid4")
    first_call_input_id = uuid4_generator()
    first_call_input_id_2 = uuid4_generator()
    second_call_input_id = uuid4_generator()
    second_call_input_id_2 = uuid4_generator()
    uuid4_generator()
    uuid4_generator()

    # GIVEN a get current weather workflow
    workflow = BasicToolCallingNodeWorkflow()

    # WHEN the workflow is executed
    terminal_event = workflow.run(Inputs(query="What's the weather like in San Francisco?"))

    # THEN the workflow is executed successfully
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert (
        terminal_event.outputs.text
        == "Based on the function call, the current temperature in San Francisco is 70 degrees celsius."
    )
    assert terminal_event.outputs.chat_history == [
        ChatMessage(
            text=None,
            role="ASSISTANT",
            content=FunctionCallChatMessageContent(
                type="FUNCTION_CALL",
                value=FunctionCallChatMessageContentValue(
                    name="get_current_weather",
                    arguments={"location": "San Francisco", "unit": "celsius"},
                    id="call_7115tNTmEACTsQRGwKpJipJK",
                ),
            ),
            source=None,
        ),
        ChatMessage(
            text=None,
            role="FUNCTION",
            content=StringChatMessageContent(
                type="STRING",
                value='"The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."',
            ),
            source="call_7115tNTmEACTsQRGwKpJipJK",
        ),
        ChatMessage(
            text="Based on the function call, the current temperature in San Francisco is 70 degrees celsius.",
            role="ASSISTANT",
            content=None,
            source=None,
        ),
    ]

    first_call = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0]
    assert first_call.kwargs == {
        "ml_model": "gpt-4o-mini",
        "input_values": [
            PromptRequestStringInput(key="question", type="STRING", value="What's the weather like in San Francisco?"),
            PromptRequestJsonInput(key="chat_history", type="JSON", value=[]),
        ],
        "input_variables": [
            VellumVariable(
                id=str(first_call_input_id),
                key="question",
                type="STRING",
                required=None,
                default=None,
                extensions=None,
            ),
            VellumVariable(
                id=str(first_call_input_id_2),
                key="chat_history",
                type="JSON",
                required=None,
                default=None,
                extensions=None,
            ),
        ],
        "parameters": PromptParameters(
            stop=[],
            temperature=0.0,
            max_tokens=4096,
            top_p=1.0,
            top_k=0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            logit_bias=None,
            custom_parameters={"mode": "updated"},
        ),
        "blocks": [
            ChatMessagePromptBlock(
                block_type="CHAT_MESSAGE",
                state=None,
                cache_config=None,
                chat_role="SYSTEM",
                chat_source=None,
                chat_message_unterminated=None,
                blocks=[
                    RichTextPromptBlock(
                        block_type="RICH_TEXT",
                        state=None,
                        cache_config=None,
                        blocks=[
                            PlainTextPromptBlock(
                                block_type="PLAIN_TEXT", state=None, cache_config=None, text="You are a weather expert"
                            )
                        ],
                    )
                ],
            ),
            ChatMessagePromptBlock(
                block_type="CHAT_MESSAGE",
                state=None,
                cache_config=None,
                chat_role="USER",
                chat_source=None,
                chat_message_unterminated=None,
                blocks=[
                    RichTextPromptBlock(
                        block_type="RICH_TEXT",
                        state=None,
                        cache_config=None,
                        blocks=[
                            VariablePromptBlock(
                                block_type="VARIABLE", state=None, cache_config=None, input_variable="question"
                            )
                        ],
                    )
                ],
            ),
            VariablePromptBlock(block_type="VARIABLE", state=None, cache_config=None, input_variable="chat_history"),
            VariablePromptBlock(
                block_type="VARIABLE", state=None, cache_config=None, input_variable="additional_blocks"
            ),
        ],
        "settings": None,
        "functions": [
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="get_current_weather",
                description="\n    Get the current weather in a given location.\n    ",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The location to get the weather for"},
                        "unit": {"type": "string", "description": "The unit of temperature"},
                    },
                    "required": ["location", "unit"],
                },
                forced=None,
                strict=None,
            )
        ],
        "expand_meta": AdHocExpandMeta(finish_reason=True),
        "request_options": mock.ANY,
    }

    second_call = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[1]
    assert second_call.kwargs == {
        "ml_model": "gpt-4o-mini",
        "input_values": [
            PromptRequestStringInput(key="question", type="STRING", value="What's the weather like in San Francisco?"),
            PromptRequestChatHistoryInput(
                key="chat_history",
                type="CHAT_HISTORY",
                value=[
                    ChatMessage(
                        text=None,
                        role="ASSISTANT",
                        content=FunctionCallChatMessageContent(
                            type="FUNCTION_CALL",
                            value=FunctionCallChatMessageContentValue(
                                name="get_current_weather",
                                arguments={"location": "San Francisco", "unit": "celsius"},
                                id="call_7115tNTmEACTsQRGwKpJipJK",
                            ),
                        ),
                        source=None,
                    ),
                    ChatMessage(
                        text=None,
                        role="FUNCTION",
                        content=StringChatMessageContent(
                            type="STRING",
                            value='"The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."',  # noqa: E501
                        ),
                        source="call_7115tNTmEACTsQRGwKpJipJK",
                    ),
                ],
            ),
        ],
        "input_variables": [
            VellumVariable(
                id=str(second_call_input_id),
                key="question",
                type="STRING",
                required=None,
                default=None,
                extensions=None,
            ),
            VellumVariable(
                id=str(second_call_input_id_2),
                key="chat_history",
                type="CHAT_HISTORY",
                required=None,
                default=None,
                extensions=None,
            ),
        ],
        "parameters": PromptParameters(
            stop=[],
            temperature=0.0,
            max_tokens=4096,
            top_p=1.0,
            top_k=0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            logit_bias=None,
            custom_parameters={"mode": "updated"},
        ),
        "blocks": [
            ChatMessagePromptBlock(
                block_type="CHAT_MESSAGE",
                state=None,
                cache_config=None,
                chat_role="SYSTEM",
                chat_source=None,
                chat_message_unterminated=None,
                blocks=[
                    RichTextPromptBlock(
                        block_type="RICH_TEXT",
                        state=None,
                        cache_config=None,
                        blocks=[
                            PlainTextPromptBlock(
                                block_type="PLAIN_TEXT", state=None, cache_config=None, text="You are a weather expert"
                            )
                        ],
                    )
                ],
            ),
            ChatMessagePromptBlock(
                block_type="CHAT_MESSAGE",
                state=None,
                cache_config=None,
                chat_role="USER",
                chat_source=None,
                chat_message_unterminated=None,
                blocks=[
                    RichTextPromptBlock(
                        block_type="RICH_TEXT",
                        state=None,
                        cache_config=None,
                        blocks=[
                            VariablePromptBlock(
                                block_type="VARIABLE", state=None, cache_config=None, input_variable="question"
                            )
                        ],
                    )
                ],
            ),
            VariablePromptBlock(block_type="VARIABLE", state=None, cache_config=None, input_variable="chat_history"),
            VariablePromptBlock(
                block_type="VARIABLE", state=None, cache_config=None, input_variable="additional_blocks"
            ),
        ],
        "settings": None,
        "functions": [
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="get_current_weather",
                description="\n    Get the current weather in a given location.\n    ",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The location to get the weather for"},
                        "unit": {"type": "string", "description": "The unit of temperature"},
                    },
                    "required": ["location", "unit"],
                },
                forced=None,
                strict=None,
            )
        ],
        "expand_meta": AdHocExpandMeta(finish_reason=True),
        "request_options": mock.ANY,
    }


def test_tool_router_node_emits_chat_history_in_prompt_inputs(
    vellum_adhoc_prompt_client, vellum_client, mock_uuid4_generator
):
    """
    Test that the ToolRouterNode emits the chat history in the prompt inputs.
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
        elif call_count == 2:
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"location": "San Diego", "unit": "celsius"},
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

    # Set up the mock to return our events
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    uuid4_generator = mock_uuid4_generator("vellum.workflows.nodes.displayable.bases.inline_prompt_node.node.uuid4")
    uuid4_generator()
    uuid4_generator()
    uuid4_generator()
    uuid4_generator()
    uuid4_generator()
    uuid4_generator()

    # GIVEN a get current weather workflow
    workflow = BasicToolCallingNodeWorkflow()

    # WHEN the workflow is executed
    events = list(
        workflow.stream(
            Inputs(query="What's the weather like in San Francisco?"), event_filter=all_workflow_event_filter
        )
    )

    tool_router_node_initiated_events = [
        e for e in events if e.name == "node.execution.initiated" and issubclass(e.body.node_definition, ToolPromptNode)
    ]

    assert len(tool_router_node_initiated_events) == 3

    first_event = tool_router_node_initiated_events[0]
    first_key = list(first_event.body.inputs.keys())[0]
    first_chat_history = first_event.body.inputs[first_key]
    assert first_chat_history == []

    second_event = tool_router_node_initiated_events[1]
    second_key = list(second_event.body.inputs.keys())[0]
    second_chat_history = second_event.body.inputs[second_key]
    assert second_chat_history == [
        ChatMessage(
            text=None,
            role="ASSISTANT",
            content=FunctionCallChatMessageContent(
                type="FUNCTION_CALL",
                value=FunctionCallChatMessageContentValue(
                    name="get_current_weather",
                    arguments={"location": "San Francisco", "unit": "celsius"},
                    id="call_7115tNTmEACTsQRGwKpJipJK",
                ),
            ),
            source=None,
        ),
        ChatMessage(
            text=None,
            role="FUNCTION",
            content=StringChatMessageContent(
                type="STRING",
                value='"The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."',
            ),
            source="call_7115tNTmEACTsQRGwKpJipJK",
        ),
    ]

    third_event = tool_router_node_initiated_events[2]
    third_key = list(third_event.body.inputs.keys())[0]
    third_chat_history = third_event.body.inputs[third_key]
    assert third_chat_history == [
        ChatMessage(
            text=None,
            role="ASSISTANT",
            content=FunctionCallChatMessageContent(
                type="FUNCTION_CALL",
                value=FunctionCallChatMessageContentValue(
                    name="get_current_weather",
                    arguments={"location": "San Francisco", "unit": "celsius"},
                    id="call_7115tNTmEACTsQRGwKpJipJK",
                ),
            ),
            source=None,
        ),
        ChatMessage(
            text=None,
            role="FUNCTION",
            content=StringChatMessageContent(
                type="STRING",
                value='"The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."',
            ),
            source="call_7115tNTmEACTsQRGwKpJipJK",
        ),
        ChatMessage(
            text=None,
            role="ASSISTANT",
            content=FunctionCallChatMessageContent(
                type="FUNCTION_CALL",
                value=FunctionCallChatMessageContentValue(
                    name="get_current_weather",
                    arguments={"location": "San Diego", "unit": "celsius"},
                    id="call_7115tNTmEACTsQRGwKpJipJK",
                ),
            ),
            source=None,
        ),
        ChatMessage(
            text=None,
            role="FUNCTION",
            content=StringChatMessageContent(
                type="STRING",
                value='"The current weather in San Diego is sunny with a temperature of 70 degrees celsius."',
            ),
            source="call_7115tNTmEACTsQRGwKpJipJK",
        ),
    ]


def test_run_workflow__string_and_function_call_outputs(vellum_adhoc_prompt_client, vellum_client):
    """
    Test that the tool calling node returns both STRING and FUNCTION_CALL outputs on first invocation.
    """

    def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())

        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
        expected_outputs: List[PromptOutput]
        if call_count == 1:
            expected_outputs = [
                StringVellumValue(value="I'll help you get the weather information."),
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

    # GIVEN a get current weather workflow
    workflow = BasicToolCallingNodeWorkflow()

    # AND the mock is set up to return our events
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN the workflow is executed
    workflow.run(Inputs(query="What's the weather like in San Francisco?"))

    # THEN the adhoc_execute_prompt_stream should be called exactly twice
    assert vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count == 2

    # AND the second call should have the correct chat_history input value
    second_call = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[1]
    chat_history_input = next(
        input_val
        for input_val in second_call.kwargs["input_values"]
        if hasattr(input_val, "key") and input_val.key == "chat_history"
    )
    assert chat_history_input.value == [
        ChatMessage(
            role="ASSISTANT",
            content=ArrayChatMessageContent(
                value=[
                    StringChatMessageContent(value="I'll help you get the weather information."),
                    FunctionCallChatMessageContent(
                        value=FunctionCallChatMessageContentValue(
                            name="get_current_weather",
                            arguments={"location": "San Francisco", "unit": "celsius"},
                            id="call_7115tNTmEACTsQRGwKpJipJK",
                        ),
                    ),
                ]
            ),
            source=None,
        ),
        ChatMessage(
            role="FUNCTION",
            content=StringChatMessageContent(
                value='"The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."'
            ),
            source="call_7115tNTmEACTsQRGwKpJipJK",
        ),
    ]


@pytest.mark.skip(reason="Testing events emission will be implemented in a follow up PR")
def test_run_workflow__emits_subworkflow_events_with_tool_call(vellum_adhoc_prompt_client, mock_uuid4_generator):
    """
    Test that the ToolCallingNode properly emits subworkflow events via _emit_subworkflow_event.
    This test should FAIL when _emit_subworkflow_event is commented out in the ToolCallingNode.
    """
    # GIVEN a get current weather workflow
    workflow = BasicToolCallingNodeWorkflow()

    # AND we know what events will be returned
    def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        expected_outputs = [StringVellumValue(value="The current temperature in New York is 75 degrees fahrenheit.")]

        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN the workflow is streamed with all event filter to capture subworkflow events
    events = list(
        workflow.stream(
            inputs=Inputs(query="What's the weather like in New York?"), event_filter=all_workflow_event_filter
        )
    )

    # THEN we should see events from the main workflow
    main_workflow_events = [e for e in events if e.parent is None]
    assert len(main_workflow_events) >= 2

    # AND we should see subworkflow events from the ToolCallingNode's internal workflow
    subworkflow_events = [
        e for e in events if e.parent is not None and hasattr(e.parent, "type") and e.parent.type == "WORKFLOW_NODE"
    ]

    assert len(subworkflow_events) > 0

    # AND the subworkflow events should have the correct parent structure
    for event in subworkflow_events:
        assert event.parent is not None
        assert event.parent.type == "WORKFLOW_NODE"
        assert event.parent.parent is not None
        assert event.parent.parent.type == "WORKFLOW"
        assert event.parent.parent.workflow_definition.name == "BasicToolCallingNodeWorkflow"


def test_tool_calling_node__tool_error_includes_stacktrace(vellum_adhoc_prompt_client, vellum_client):
    """
    Test that when a tool errors, the rejected event includes a stacktrace.
    """
    from typing import Annotated

    def error_tool(location: Annotated[str, "The location to get the weather for"]) -> str:
        """
        A tool that always throws an error.
        """
        raise ValueError("This tool always fails")

    def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())

        expected_outputs = [
            FunctionCallVellumValue(
                value=FunctionCall(
                    arguments={"location": "San Francisco"},
                    id="call_error_tool",
                    name="error_tool",
                    state="FULFILLED",
                ),
            ),
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

    class ErrorToolCallingNode(ToolCallingNode):
        ml_model = "gpt-4o-mini"
        blocks = [
            ChatMessagePromptBlock(
                chat_role="USER",
                blocks=[
                    RichTextPromptBlock(
                        blocks=[
                            PlainTextPromptBlock(text="Call the error tool"),
                        ],
                    ),
                ],
            ),
        ]
        functions = [error_tool]

    class ErrorToolWorkflow(BaseWorkflow):
        graph = ErrorToolCallingNode

    workflow = ErrorToolWorkflow()

    # WHEN the workflow is run
    events = list(workflow.stream(event_filter=all_workflow_event_filter))

    # THEN we should find a node rejection event
    node_rejected_events = [e for e in events if e.name == "node.execution.rejected"]
    assert len(node_rejected_events) > 0

    # AND the rejected event should have a stacktrace
    rejected_event = node_rejected_events[-1]
    assert rejected_event.body.stacktrace is not None
    assert "NodeException" in rejected_event.body.stacktrace
    assert "Error executing function 'error_tool': This tool always fails" in rejected_event.body.stacktrace


def test_function_node_execution_inputs_excludes_function_call_output(vellum_adhoc_prompt_client, mock_uuid4_generator):
    """Test that FunctionNode execution events exclude function_call_output from inputs."""

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

    uuid4_generator = mock_uuid4_generator("vellum.workflows.nodes.displayable.bases.inline_prompt_node.node.uuid4")
    uuid4_generator()
    uuid4_generator()

    # GIVEN a workflow with a function node
    workflow = BasicToolCallingNodeWorkflow()

    # WHEN the workflow is executed
    events = list(workflow.stream(event_filter=all_workflow_event_filter, inputs=Inputs(query="What's the weather?")))

    # THEN find the FunctionNode execution initiated event
    function_node_events = [
        e
        for e in events
        if isinstance(e, NodeExecutionInitiatedEvent)
        and e.node_definition.__name__ == "FunctionNode_get_current_weather"
    ]

    assert len(function_node_events) > 0, "Expected at least one FunctionNode execution event"

    # AND the event inputs should NOT include function_call_output
    function_node_event = function_node_events[0]
    serialized_inputs = function_node_event.body.model_dump(mode="json")["inputs"]
    # AND the inputs should only include arguments
    assert serialized_inputs == {
        "arguments": {
            "location": "San Francisco",
            "unit": "celsius",
        },
    }


def test_function_node_execution_inputs_uses_current_prompt_output_index(
    vellum_adhoc_prompt_client, mock_uuid4_generator
):
    """
    Test that FunctionNode execution events serialize arguments from the current function call
    based on state.current_prompt_output_index, not always the first function call.
    """

    def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
        expected_outputs: List[PromptOutput]
        if call_count == 1:
            expected_outputs = [
                StringVellumValue(value="I'll help you with the weather."),
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"location": "San Francisco", "unit": "celsius"},
                        id="call_first",
                        name="get_current_weather",
                        state="FULFILLED",
                    ),
                ),
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"location": "New York", "unit": "fahrenheit"},
                        id="call_second",
                        name="get_current_weather",
                        state="FULFILLED",
                    ),
                ),
            ]
        else:
            expected_outputs = [
                StringVellumValue(value="The weather in San Francisco is 70°C and in New York is 75°F.")
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

    uuid4_generator = mock_uuid4_generator("vellum.workflows.nodes.displayable.bases.inline_prompt_node.node.uuid4")
    uuid4_generator()
    uuid4_generator()

    # GIVEN a workflow with a function node
    workflow = BasicToolCallingNodeWorkflow()

    # WHEN the workflow is executed with a prompt that returns multiple function calls
    events = list(workflow.stream(event_filter=all_workflow_event_filter, inputs=Inputs(query="What's the weather?")))

    # THEN find all FunctionNode execution initiated events
    function_node_events = [
        e
        for e in events
        if isinstance(e, NodeExecutionInitiatedEvent)
        and e.node_definition.__name__ == "FunctionNode_get_current_weather"
    ]

    assert len(function_node_events) == 2, "Expected two FunctionNode execution events"

    # AND the first function node event should have the first function call's arguments
    first_event_inputs = function_node_events[0].body.model_dump(mode="json")["inputs"]
    assert first_event_inputs == {
        "arguments": {
            "location": "San Francisco",
            "unit": "celsius",
        },
    }

    # AND the second function node event should have the second function call's arguments
    second_event_inputs = function_node_events[1].body.model_dump(mode="json")["inputs"]
    assert second_event_inputs == {
        "arguments": {
            "location": "New York",
            "unit": "fahrenheit",
        },
    }
