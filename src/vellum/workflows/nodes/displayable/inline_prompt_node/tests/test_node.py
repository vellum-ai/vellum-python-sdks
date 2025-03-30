import pytest
from dataclasses import dataclass
import json
from uuid import UUID, uuid4
from typing import Any, Iterator, List

from httpx import Response

from vellum.client.core.api_error import ApiError
from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.chat_message import ChatMessage
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
from vellum.workflows.events.types import (
    CodeResourceDefinition,
    NodeParentContext,
    WorkflowDeploymentParentContext,
    WorkflowParentContext,
)
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
    ]
    assert len(mock_api.call_args.kwargs["input_variables"]) == 4


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
def test_inline_prompt_node__parent_context(mock_httpx_transport):
    # GIVEN a prompt node
    class MyNode(InlinePromptNode):
        ml_model = "gpt-4o"
        blocks = []
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

    # AND a complex parent context
    # TODO: We were able to confirm that this caused our serialization to hang, but don't know why yet.
    # We should try to reduce this example further to isolate a minimal example that reproduces the issue.
    trace_id = uuid4()
    parent_context = NodeParentContext(
        span_id=UUID("d697f8c8-b363-4154-8469-eb4f9fb5e445"),
        parent=WorkflowParentContext(
            span_id=UUID("a0c68884-22c3-4ac9-8476-8747884d80e1"),
            parent=NodeParentContext(
                span_id=UUID("46163407-71f7-40f2-9f66-872d4b338fcc"),
                parent=WorkflowParentContext(
                    span_id=UUID("0ddf01e7-d0c3-426c-af27-d8bfb22fcdd5"),
                    parent=NodeParentContext(
                        span_id=UUID("79a6c926-b5f3-4ede-b2f8-4bb6f0c086ba"),
                        parent=WorkflowParentContext(
                            span_id=UUID("530a56fe-90fd-4f4c-b905-457975fb3e10"),
                            parent=WorkflowDeploymentParentContext(
                                span_id=UUID("3e10a8c2-558c-4ef7-926d-7b79ebc7cba9"),
                                parent=NodeParentContext(
                                    span_id=UUID("a3cd4086-c0b9-4dff-88f3-3e2191b8a2a7"),
                                    parent=WorkflowParentContext(
                                        span_id=UUID("c2ba7577-8d24-49b1-aa92-b9ace8244090"),
                                        workflow_definition=CodeResourceDefinition(
                                            id=UUID("2e2d5c56-49b7-48b5-82fa-e80e72768b9c"),
                                            name="Workflow",
                                            module=["e81a6124-2c57-4c39-938c-ab6059059ff2", "workflow"],
                                        ),
                                    ),
                                    node_definition=CodeResourceDefinition(
                                        id=UUID("23d25675-f377-4450-916f-39ebee5c8ea9"),
                                        name="SubworkflowDeployment",
                                        module=[
                                            "e81a6124-2c57-4c39-938c-ab6059059ff2",
                                            "nodes",
                                            "subworkflow_deployment",
                                        ],
                                    ),
                                ),
                                deployment_id=UUID("cfc99610-2869-4506-b106-3fd7ce0bbb15"),
                                deployment_name="my-deployment",
                                deployment_history_item_id=UUID("13f31aae-29fd-4066-a4ec-c7687faebae3"),
                                release_tag_id=UUID("2d03987a-dcb5-49b9-981e-5e871c8f5d97"),
                                release_tag_name="LATEST",
                                external_id=None,
                                metadata=None,
                                workflow_version_id=UUID("7eaae816-b5f3-436d-8597-e8c3e4a32958"),
                            ),
                            workflow_definition=CodeResourceDefinition(
                                id=UUID("2e2d5c56-49b7-48b5-82fa-e80e72768b9c"),
                                name="Workflow",
                                module=["3e10a8c2-558c-4ef7-926d-7b79ebc7cba9", "workflow"],
                            ),
                        ),
                        node_definition=CodeResourceDefinition(
                            id=UUID("42c8adc2-a0d6-499e-81a4-e2e02d7beba9"),
                            name="MyNode",
                            module=[
                                "3e10a8c2-558c-4ef7-926d-7b79ebc7cba9",
                                "nodes",
                                "my_node",
                            ],
                        ),
                    ),
                    workflow_definition=CodeResourceDefinition(
                        id=UUID("b8563da0-7fd4-42e0-a75e-9ef037fca5a1"),
                        name="MyNodeWorkflow",
                        module=[
                            "3e10a8c2-558c-4ef7-926d-7b79ebc7cba9",
                            "nodes",
                            "my_node",
                            "workflow",
                        ],
                    ),
                ),
                node_definition=CodeResourceDefinition(
                    id=UUID("d44aee53-3b6e-41fd-8b7a-908cb2c77821"),
                    name="RetryNode",
                    module=[
                        "3e10a8c2-558c-4ef7-926d-7b79ebc7cba9",
                        "nodes",
                        "my_node",
                        "nodes",
                        "my_prompt",
                        "MyPrompt",
                        "<adornment>",
                    ],
                ),
            ),
            workflow_definition=CodeResourceDefinition(
                id=UUID("568a28dd-7134-436e-a5f4-790675212b51"),
                name="Subworkflow",
                module=["vellum", "workflows", "nodes", "utils"],
            ),
        ),
        node_definition=CodeResourceDefinition(
            id=UUID("86a34e5c-2652-49f0-9f9e-c653cf70029a"),
            name="MyPrompt",
            module=[
                "3e10a8c2-558c-4ef7-926d-7b79ebc7cba9",
                "nodes",
                "my_node",
                "nodes",
                "my_prompt",
            ],
        ),
    )

    # WHEN the node is run
    with execution_context(
        parent_context=parent_context,
        trace_id=trace_id,
    ):
        outputs = list(MyNode().run())

    # THEN the last output is as expected
    assert outputs[-1].value == "Test"

    # AND the prompt is executed with the correct execution context
    call_request_args = mock_httpx_transport.handle_request.call_args_list[0][0][0]
    request_execution_context = json.loads(call_request_args.read().decode("utf-8"))["execution_context"]
    assert request_execution_context["trace_id"] == str(trace_id)
    assert request_execution_context["parent_context"]
