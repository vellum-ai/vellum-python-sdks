"""Tests for ChatMessageTrigger serialization."""

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
    triggers = serialized_workflow["triggers"]
    assert len(triggers) == 1
    trigger = triggers[0]
    assert trigger["id"] == "9e14c49b-c6d9-4fe5-9ff2-835fd695fe5f"
    assert trigger["type"] == "CHAT_MESSAGE"

    # AND the exec_config should have both output and state
    exec_config = trigger["exec_config"]
    assert exec_config["output"] == {
        "type": "WORKFLOW_OUTPUT",
        "output_variable_id": "cc1208e9-c043-47f4-abea-c01ac0dbf04c",
    }
    assert "state" in exec_config
    assert "state_variable_id" in exec_config["state"]


class ResponseNode(BaseNode):
    """Node that returns a simple response."""

    class Outputs(BaseNode.Outputs):
        response: str = "Hello!"


class ChatTriggerWithoutOutputOrState(ChatMessageTrigger):
    """Chat trigger without Config.output or Config.state specified."""

    pass


class WorkflowWithUnspecifiedChatTriggerConfig(BaseWorkflow[BaseInputs, BaseState]):
    """Workflow using ChatTrigger without output or state specified."""

    graph = ChatTriggerWithoutOutputOrState >> ResponseNode

    class Outputs(BaseWorkflow.Outputs):
        response = ResponseNode.Outputs.response


def test_chat_message_trigger_validation__output_not_specified():
    """
    Tests that serialization adds TriggerValidationError when Chat Trigger output is not specified.
    """

    # GIVEN a Workflow that uses a ChatMessageTrigger without Config.output specified
    workflow_display = get_workflow_display(workflow_class=WorkflowWithUnspecifiedChatTriggerConfig)

    # WHEN we serialize the workflow
    workflow_display.serialize()

    # THEN the display_context should contain a TriggerValidationError for output
    errors = list(workflow_display.display_context.errors)
    output_errors = [e for e in errors if "output must be specified" in str(e)]
    assert len(output_errors) == 1

    # AND the error should be a TriggerValidationError with the expected message
    error = output_errors[0]
    assert isinstance(error, TriggerValidationError)
    assert "Chat Trigger output must be specified" in str(error)


def test_chat_message_trigger_validation__state_not_specified():
    """
    Tests that serialization adds TriggerValidationError when Chat Trigger state is not specified.
    """

    # GIVEN a Workflow that uses a ChatMessageTrigger without Config.state specified
    workflow_display = get_workflow_display(workflow_class=WorkflowWithUnspecifiedChatTriggerConfig)

    # WHEN we serialize the workflow
    workflow_display.serialize()

    # THEN the display_context should contain a TriggerValidationError for state
    errors = list(workflow_display.display_context.errors)
    state_errors = [e for e in errors if "state must be specified" in str(e)]
    assert len(state_errors) == 1

    # AND the error should be a TriggerValidationError with the expected message
    error = state_errors[0]
    assert isinstance(error, TriggerValidationError)
    assert "Chat Trigger state must be specified" in str(error)
