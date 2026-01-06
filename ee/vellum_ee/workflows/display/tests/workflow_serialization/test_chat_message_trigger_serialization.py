"""Tests for ChatMessageTrigger serialization."""

from typing import List

from pydantic import Field

from vellum.client.types import ChatMessage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.chat_message import ChatMessageTrigger
from vellum_ee.workflows.display.utils.exceptions import TriggerValidationError
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
                    "type": "ARRAY",
                    "required": True,
                    "default": {
                        "type": "ARRAY",
                        "value": None,
                    },
                    "extensions": None,
                    "schema": None,
                }
            ],
            "exec_config": {
                "output": {
                    "type": "WORKFLOW_OUTPUT",
                    "output_variable_id": "cc1208e9-c043-47f4-abea-c01ac0dbf04c",
                },
            },
            "display_data": {
                "label": "Chat Message",
                "position": {
                    "x": 0.0,
                    "y": 0.0,
                },
                "z_index": 0,
                "icon": "vellum:icon:message-dots",
                "color": "blue",
            },
        }
    ]


class ResponseNode(BaseNode):
    """Node that returns a simple response."""

    class Outputs(BaseNode.Outputs):
        response: str = "Hello!"


class ChatTriggerWithoutOutput(ChatMessageTrigger):
    """Chat trigger without Config.output specified."""

    pass


class WorkflowWithUnspecifiedChatTriggerOutput(BaseWorkflow[BaseInputs, BaseState]):
    """Workflow using ChatTrigger without output specified."""

    graph = ChatTriggerWithoutOutput >> ResponseNode

    class Outputs(BaseWorkflow.Outputs):
        response = ResponseNode.Outputs.response


def test_chat_message_trigger_validation__output_not_specified():
    """
    Tests that serialization adds TriggerValidationError to errors when Chat Trigger output is not specified.
    """

    # GIVEN a Workflow that uses a ChatMessageTrigger without Config.output specified
    workflow_display = get_workflow_display(workflow_class=WorkflowWithUnspecifiedChatTriggerOutput)

    # WHEN we serialize the workflow
    workflow_display.serialize()

    # THEN the display_context should contain a TriggerValidationError
    errors = list(workflow_display.display_context.errors)
    assert len(errors) == 1

    # AND the error should be a TriggerValidationError with the expected message
    error = errors[0]
    assert isinstance(error, TriggerValidationError)
    assert "Chat Trigger output must be specified" in str(error)


def test_chat_message_trigger_serialization__custom_state():
    """Tests that ChatMessageTrigger serializes custom state reference correctly."""

    # GIVEN a state with a custom chat history attribute
    class CustomChatHistoryState(BaseState):
        messages: List[ChatMessage] = Field(default_factory=list)

    # AND a trigger with a custom state reference
    class CustomStateTrigger(ChatMessageTrigger):
        class Config(ChatMessageTrigger.Config):
            state = CustomChatHistoryState.messages

    # AND a simple node
    class ResponseNodeCustom(BaseNode):
        class Outputs(BaseNode.Outputs):
            response: str = "Hello!"

    # AND a workflow using the custom trigger
    class CustomStateWorkflow(BaseWorkflow[BaseInputs, CustomChatHistoryState]):
        graph = CustomStateTrigger >> ResponseNodeCustom

        class Outputs(BaseWorkflow.Outputs):
            response = ResponseNodeCustom.Outputs.response

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=CustomStateWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the trigger should have the state reference in exec_config
    triggers = serialized_workflow["triggers"]
    assert len(triggers) == 1
    assert triggers[0]["type"] == "CHAT_MESSAGE"
    exec_config = triggers[0]["exec_config"]
    assert "state" in exec_config
    assert "state_variable_id" in exec_config["state"]


def test_chat_message_trigger_serialization__default_state():
    """Tests that ChatMessageTrigger does not serialize state when using default."""

    # GIVEN a state with default chat_history attribute
    class DefaultChatHistoryState(BaseState):
        chat_history: List[ChatMessage] = Field(default_factory=list)

    # AND a trigger with no state reference (uses default "chat_history")
    class DefaultStateTrigger(ChatMessageTrigger):
        pass

    # AND a simple node
    class ResponseNodeDefault(BaseNode):
        class Outputs(BaseNode.Outputs):
            response: str = "Hello!"

    # AND a workflow using the default trigger
    class DefaultStateWorkflow(BaseWorkflow[BaseInputs, DefaultChatHistoryState]):
        graph = DefaultStateTrigger >> ResponseNodeDefault

        class Outputs(BaseWorkflow.Outputs):
            response = ResponseNodeDefault.Outputs.response

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=DefaultStateWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the trigger should not have exec_config (since no state reference is set)
    triggers = serialized_workflow["triggers"]
    assert len(triggers) == 1
    assert triggers[0]["type"] == "CHAT_MESSAGE"
    assert "exec_config" not in triggers[0]
