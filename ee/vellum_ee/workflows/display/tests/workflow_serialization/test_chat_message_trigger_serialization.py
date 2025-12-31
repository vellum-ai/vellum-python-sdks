"""Tests for ChatMessageTrigger serialization."""

from typing import List

from pydantic import Field

from vellum.client.types import ChatMessage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.references import LazyReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.chat_message import ChatMessageTrigger
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.chat_message_trigger_execution.workflows.simple_chat_workflow import SimpleChatWorkflow


def test_simple_chat_workflow_serialization():
    """SimpleChatWorkflow from tests/workflows serializes correctly with ChatMessageTrigger."""

    # GIVEN a Workflow that uses a ChatMessageTrigger
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=SimpleChatWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
        "triggers",
    }

    # AND the triggers should be serialized correctly
    assert serialized_workflow["triggers"] == [
        {
            "id": "9e14c49b-c6d9-4fe5-9ff2-835fd695fe5f",
            "type": "CHAT_MESSAGE",
            "attributes": [
                {
                    "id": "5edbfd78-b634-4305-b2ad-d9feecbd5e5f",
                    "key": "message",
                    "type": "JSON",
                    "required": True,
                    "default": {
                        "type": "JSON",
                        "value": None,
                    },
                    "extensions": None,
                    "schema": None,
                }
            ],
            "exec_config": {
                "output": {
                    "type": "NODE_OUTPUT",
                    "node_id": "6c43f557-304c-4f08-a8fd-13d1fb02d96a",
                    "node_output_id": "14f1265b-d5fb-4b60-b06b-9012029f6c6c",
                },
            },
            "display_data": {
                "label": "Chat Message",
                "position": {
                    "x": 0.0,
                    "y": 0.0,
                },
                "z_index": 0,
                "icon": "vellum:icon:message",
                "color": "blue",
            },
        }
    ]


def test_chat_message_trigger_with_default_value_serialization():
    """ChatMessageTrigger with default attribute value serializes the default correctly."""

    # GIVEN a ChatMessageTrigger with a default message value
    class ChatStateWithDefault(BaseState):
        chat_history: List[ChatMessage] = Field(default_factory=list)

    class ResponseNodeWithDefault(BaseNode):
        class Outputs(BaseNode.Outputs):
            response: str = "Hello from assistant!"

    class ChatTriggerWithDefault(ChatMessageTrigger):
        message: str = "Hello"

        class Config(ChatMessageTrigger.Config):
            output = LazyReference(lambda: WorkflowWithDefaultTrigger.Outputs.response)  # type: ignore[has-type]

    class WorkflowWithDefaultTrigger(BaseWorkflow[BaseInputs, ChatStateWithDefault]):
        graph = ChatTriggerWithDefault >> ResponseNodeWithDefault

        class Outputs(BaseWorkflow.Outputs):
            response = ResponseNodeWithDefault.Outputs.response

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=WorkflowWithDefaultTrigger)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the triggers should be serialized correctly
    triggers = serialized_workflow["triggers"]
    assert len(triggers) == 1

    # AND the trigger attribute should have the default value serialized
    trigger = triggers[0]
    assert trigger["type"] == "CHAT_MESSAGE"

    attributes = trigger["attributes"]
    assert len(attributes) == 1

    message_attr = attributes[0]
    assert message_attr["key"] == "message"
    # The type is STRING because the subclass narrows the type from Union[str, ChatMessageContent] to str
    assert message_attr["type"] == "STRING"

    # AND the default value should be "Hello" serialized as STRING
    assert message_attr["default"] == {"type": "STRING", "value": "Hello"}
