import pytest
import json
from uuid import uuid4
from typing import Any, Iterator, List

from httpx import Response

from vellum.client.types.chat_history_input_request import ChatHistoryInputRequest
from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.chat_message_request import ChatMessageRequest
from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.json_input_request import JsonInputRequest
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.workflows.context import execution_context
from vellum.workflows.nodes.displayable.prompt_deployment_node.node import PromptDeploymentNode


@pytest.mark.parametrize("ChatMessageClass", [ChatMessageRequest, ChatMessage])
def test_run_node__chat_history_input(vellum_client, ChatMessageClass):
    """Confirm that we can successfully invoke a Prompt Deployment Node that uses Chat History Inputs"""

    # GIVEN a Prompt Deployment Node
    class ExamplePromptDeploymentNode(PromptDeploymentNode):
        deployment = "example_prompt_deployment"
        prompt_inputs = {
            "chat_history": [ChatMessageClass(role="USER", text="Hello, how are you?")],
        }

    # AND we know what the Prompt Deployment will respond with
    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=[
                    StringVellumValue(value="Great!"),
                ],
            ),
        ]
        yield from events

    vellum_client.execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN we run the node
    node = ExamplePromptDeploymentNode()
    events = list(node.run())

    # THEN the node should have completed successfully
    assert events[-1].value == "Great!"

    # AND we should have invoked the Prompt Deployment with the expected inputs
    call_kwargs = vellum_client.execute_prompt_stream.call_args.kwargs
    assert call_kwargs["inputs"] == [
        ChatHistoryInputRequest(
            name="chat_history", value=[ChatMessageRequest(role="USER", text="Hello, how are you?")]
        ),
    ]


@pytest.mark.parametrize(
    "input_value",
    [
        ["apple", "banana", "cherry"],
        [],
    ],
    ids=["non_empty_array", "empty_array"],
)
def test_run_node__any_array_input(vellum_client, input_value):
    """Confirm that we can successfully invoke a Prompt Deployment Node that uses any array input"""

    # GIVEN a Prompt Deployment Node
    class ExamplePromptDeploymentNode(PromptDeploymentNode):
        deployment = "example_prompt_deployment"
        prompt_inputs = {
            "fruits": input_value,
        }

    # AND we know what the Prompt Deployment will respond with
    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=[
                    StringVellumValue(value="Great!"),
                ],
            ),
        ]
        yield from events

    vellum_client.execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN we run the node
    node = ExamplePromptDeploymentNode()
    events = list(node.run())

    # THEN the node should have completed successfully
    assert events[-1].value == "Great!"

    # AND we should have invoked the Prompt Deployment with the expected inputs
    call_kwargs = vellum_client.execute_prompt_stream.call_args.kwargs
    assert call_kwargs["inputs"] == [
        JsonInputRequest(name="fruits", value=input_value),
    ]


@pytest.mark.timeout(5)
def test_prompt_deployment_node__parent_context_serialization(mock_httpx_transport, mock_complex_parent_context):
    # GIVEN a prompt deployment node
    class MyNode(PromptDeploymentNode):
        deployment = "example_prompt_deployment"
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

    # WHEN the node is run with a complex parent context
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
    request_execution_context = json.loads(call_request_args.read().decode("utf-8"))["execution_context"]
    assert request_execution_context["trace_id"] == str(trace_id)
    assert request_execution_context["parent_context"]
