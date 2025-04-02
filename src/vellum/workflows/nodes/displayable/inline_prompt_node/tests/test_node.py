import pytest
from dataclasses import dataclass
import json
from uuid import uuid4
from typing import Any, Iterator, List

from httpx import Response

from vellum.client.core.api_error import ApiError
from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.chat_message_request import ChatMessageRequest
from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.function_definition import FunctionDefinition
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.prompt_request_chat_history_input import PromptRequestChatHistoryInput
from vellum.client.types.prompt_request_json_input import PromptRequestJsonInput
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.workflows.context import execution_context
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode


def test_inline_prompt_node__json_inputs(vellum_adhoc_prompt_client):
    # GIVEN a prompt node with various inputs
    @dataclass
    class MyDataClass:
        hello: str

    class MyPydantic(UniversalBaseModel):
        example: str

    class MyNode(InlinePromptNode):
        ml_model = "gpt-4o"
        blocks = []
        prompt_inputs = {
            "a_dict": {"foo": "bar"},
            "a_list": [1, 2, 3],
            "a_dataclass": MyDataClass(hello="world"),
            "a_pydantic": MyPydantic(example="example"),
            "an_empty_list": [],
        }

    # AND a known response from invoking an inline prompt
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="Test"),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN the node is run
    list(MyNode().run())

    # THEN the prompt is executed with the correct inputs
    mock_api = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream
    assert mock_api.call_count == 1
    assert mock_api.call_args.kwargs["input_values"] == [
        PromptRequestJsonInput(key="a_dict", type="JSON", value={"foo": "bar"}),
        PromptRequestJsonInput(key="a_list", type="JSON", value=[1, 2, 3]),
        PromptRequestJsonInput(key="a_dataclass", type="JSON", value={"hello": "world"}),
        PromptRequestJsonInput(key="a_pydantic", type="JSON", value={"example": "example"}),
        PromptRequestJsonInput(key="an_empty_list", type="JSON", value=[]),
    ]
    assert len(mock_api.call_args.kwargs["input_variables"]) == 5


def test_inline_prompt_node__function_definitions(vellum_adhoc_prompt_client):
    # GIVEN a function definition
    def my_function(foo: str, bar: int) -> None:
        pass

    # AND a prompt node with a accepting that function definition
    class MyNode(InlinePromptNode):
        ml_model = "gpt-4o"
        functions = [my_function]
        blocks = []

    # AND a known response from invoking an inline prompt
    expected_outputs: List[PromptOutput] = [
        FunctionCallVellumValue(value=FunctionCall(name="my_function", arguments={"foo": "hello", "bar": 1})),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN the node is run
    outputs = list(MyNode().run())

    # THEN the prompt is executed with the correct inputs
    mock_api = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream
    assert mock_api.call_count == 1
    assert mock_api.call_args.kwargs["functions"] == [
        FunctionDefinition(
            name="my_function",
            parameters={
                "type": "object",
                "properties": {
                    "foo": {"type": "string"},
                    "bar": {"type": "integer"},
                },
                "required": ["foo", "bar"],
            },
        ),
    ]
    assert (
        outputs[-1].value
        == """{
    "arguments": {
        "foo": "hello",
        "bar": 1
    },
    "id": null,
    "name": "my_function"
}"""
    )


@pytest.mark.parametrize(
    ["exception", "expected_code", "expected_message"],
    [
        (
            ApiError(status_code=404, body={"detail": "Model not found"}),
            WorkflowErrorCode.INVALID_INPUTS,
            "Model not found",
        ),
        (
            ApiError(status_code=404, body={"message": "Model not found"}),
            WorkflowErrorCode.INVALID_INPUTS,
            "Failed to execute Prompt",
        ),
        (
            ApiError(status_code=404, body="Model not found"),
            WorkflowErrorCode.INTERNAL_ERROR,
            "Failed to execute Prompt",
        ),
        (
            ApiError(status_code=None, body={"detail": "Model not found"}),
            WorkflowErrorCode.INTERNAL_ERROR,
            "Failed to execute Prompt",
        ),
        (
            ApiError(status_code=500, body={"detail": "Model not found"}),
            WorkflowErrorCode.INTERNAL_ERROR,
            "Failed to execute Prompt",
        ),
    ],
    ids=["404", "invalid_dict", "invalid_body", "no_status_code", "500"],
)
def test_inline_prompt_node__api_error__invalid_inputs_node_exception(
    vellum_adhoc_prompt_client, exception, expected_code, expected_message
):
    # GIVEN a prompt node with an invalid model name
    class MyNode(InlinePromptNode):
        ml_model = "my-invalid-model"
        blocks = []

    # AND the adhoc prompt client raises a 4xx error
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = exception

    # WHEN the node is run
    with pytest.raises(NodeException) as e:
        list(MyNode().run())

    # THEN the node raises the correct NodeException
    assert e.value.code == expected_code
    assert e.value.message == expected_message


def test_inline_prompt_node__chat_history_inputs(vellum_adhoc_prompt_client):
    # GIVEN a prompt node with a chat history input
    class MyNode(InlinePromptNode):
        ml_model = "gpt-4o"
        blocks = []
        prompt_inputs = {
            "chat_history": [ChatMessageRequest(role="USER", text="Hello, how are you?")],
        }

    # AND a known response from invoking an inline prompt
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="Great!"),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN the node is run
    events = list(MyNode().run())

    # THEN the prompt is executed with the correct inputs
    assert events[-1].value == "Great!"

    # AND the prompt is executed with the correct inputs
    mock_api = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream
    assert mock_api.call_count == 1
    assert mock_api.call_args.kwargs["input_values"] == [
        PromptRequestChatHistoryInput(
            key="chat_history",
            type="CHAT_HISTORY",
            value=[ChatMessage(role="USER", text="Hello, how are you?")],
        ),
    ]
    assert mock_api.call_args.kwargs["input_variables"][0].type == "CHAT_HISTORY"


@pytest.mark.timeout(5)
def test_inline_prompt_node__parent_context(mock_httpx_transport, mock_complex_parent_context):
    # GIVEN a prompt node
    class MyNode(InlinePromptNode):
        ml_model = "gpt-4o"
        blocks = [ChatMessagePromptBlock(chat_role="USER", blocks=[])]
        prompt_inputs = {}

    # AND a known response from the httpx client
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="Test"),
    ]
    execution_id = str(uuid4())
    events: List[ExecutePromptEvent] = [
        InitiatedExecutePromptEvent(execution_id=execution_id),
        FulfilledExecutePromptEvent(
            execution_id=execution_id,
            outputs=expected_outputs,
        ),
    ]
    text = "\n".join(e.model_dump_json() for e in events)

    mock_httpx_transport.handle_request.return_value = Response(
        status_code=200,
        text=text,
    )

    # WHEN the node is run with the complex parent context
    trace_id = uuid4()
    with execution_context(
        parent_context=mock_complex_parent_context,
        trace_id=trace_id,
    ):
        outputs = list(MyNode().run())

    # THEN the last output is as expected
    assert outputs[-1].value == "Test"

    # AND the prompt is executed with the correct execution context
    call_request_args = mock_httpx_transport.handle_request.call_args_list[0][0][0]
    call_request = json.loads(call_request_args.read().decode("utf-8"))
    request_execution_context = call_request["execution_context"]
    assert request_execution_context["trace_id"] == str(trace_id)
    assert request_execution_context["parent_context"]

    # AND the blocks are serialized as expected
    assert call_request["blocks"] == [
        {
            "block_type": "CHAT_MESSAGE",
            "chat_role": "USER",
            "blocks": [],
        }
    ]
