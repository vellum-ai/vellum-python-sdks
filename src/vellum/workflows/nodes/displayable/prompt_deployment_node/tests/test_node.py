import pytest
from uuid import uuid4
from typing import Any, Iterator, List

from vellum.client.types.chat_history_input_request import ChatHistoryInputRequest
from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.chat_message_request import ChatMessageRequest
from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.json_input_request import JsonInputRequest
from vellum.client.types.string_vellum_value import StringVellumValue
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


def test_run_node__any_array_input(vellum_client):
    """Confirm that we can successfully invoke a Prompt Deployment Node that uses any array input"""

    # GIVEN a Prompt Deployment Node
    class ExamplePromptDeploymentNode(PromptDeploymentNode):
        deployment = "example_prompt_deployment"
        prompt_inputs = {
            "fruits": ["apple", "banana", "cherry"],
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
        JsonInputRequest(name="fruits", value=["apple", "banana", "cherry"]),
    ]
