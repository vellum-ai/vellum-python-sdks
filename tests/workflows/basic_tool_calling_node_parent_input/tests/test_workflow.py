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

from tests.workflows.basic_tool_calling_node_parent_input.workflow import (
    BasicToolCallingNodeParentInputWorkflow,
    ParentInputs,
)


def test_tool_calling_node_with_parent_inputs(vellum_adhoc_prompt_client, mock_uuid4_generator):
    """
    Test that a tool calling node can receive inputs from parent workflow and user-defined inputs.
    """

    def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())

        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
        expected_outputs: List[PromptOutput]
        if call_count == 1:
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"populated_input": "Hello from user"},
                        id="call_7115tNTmEACTsQRGwKpJipJK",
                        name="get_string",
                    ),
                ),
            ]
        else:
            expected_outputs = [
                StringVellumValue(
                    value="Based on the function call, the result is: This is the parent input: Hello from parent and this is the populated input: Hello from user"  # noqa: E501
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
    uuid4_generator()
    uuid4_generator()

    # GIVEN a parent workflow with tool calling node that receives inputs from parent
    workflow = BasicToolCallingNodeParentInputWorkflow()

    # WHEN the workflow is executed with parent inputs
    terminal_event = workflow.run(inputs=ParentInputs(parent_input="Hello from parent"))

    # THEN the workflow is executed successfully
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert (
        terminal_event.outputs.text
        == "Based on the function call, the result is: This is the parent input: Hello from parent and this is the populated input: Hello from user"  # noqa: E501
    )
    assert terminal_event.outputs.chat_history == [
        ChatMessage(
            text=None,
            role="ASSISTANT",
            content=FunctionCallChatMessageContent(
                type="FUNCTION_CALL",
                value=FunctionCallChatMessageContentValue(
                    name="get_string",
                    arguments={"populated_input": "Hello from user"},
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
                value='"This is the parent input: Hello from parent, this is the dummy input: dummy, and this is the populated input: Hello from user"',  # noqa: E501
            ),
            source="call_7115tNTmEACTsQRGwKpJipJK",
        ),
        ChatMessage(
            text="Based on the function call, the result is: This is the parent input: Hello from parent and this is the populated input: Hello from user",  # noqa: E501
            role="ASSISTANT",
            content=None,
            source=None,
        ),
    ]

    # AND the function was called with the correct parameters
    first_call = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0]
    functions = first_call.kwargs["functions"][0]
    assert functions == FunctionDefinition(
        state=None,
        cache_config=None,
        name="get_string",
        description="\n    Get a string with the parent input, dummy input, and the populated input.\n    ",
        parameters={
            "type": "object",
            "properties": {"populated_input": {"type": "string"}},
            "required": ["populated_input"],
        },
        forced=None,
        strict=None,
    )
