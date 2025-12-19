"""Tests for ChatMessageTrigger serialization."""

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.chat_message_trigger_execution.workflows.simple_chat_workflow import SimpleChatWorkflow


def test_simple_chat_workflow_serialization():
    """SimpleChatWorkflow from tests/workflows serializes correctly with ChatMessageTrigger."""

    # WHEN we serialize the SimpleChatWorkflow
    workflow_display = get_workflow_display(workflow_class=SimpleChatWorkflow)
    result: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert result.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
        "triggers",
    }

    # AND the trigger should be serialized correctly
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1

    trigger = triggers[0]
    assert isinstance(trigger, dict)
    assert trigger["type"] == "CHAT_MESSAGE"

    # AND the trigger should have the message attribute
    attributes = trigger["attributes"]
    assert isinstance(attributes, list)
    assert len(attributes) == 1
    attribute_keys = {attr["key"] for attr in attributes if isinstance(attr, dict)}
    assert attribute_keys == {"message"}

    # AND the message attribute should be serialized as JSON type (due to complex Union type)
    message_attr = next(attr for attr in attributes if attr["key"] == "message")
    assert message_attr["type"] == "JSON"

    # AND there should be NO ENTRYPOINT node (trigger-sourced workflow)
    workflow_raw_data = result["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)
    nodes = workflow_raw_data["nodes"]
    assert isinstance(nodes, list)
    entrypoint_nodes = [n for n in nodes if isinstance(n, dict) and n.get("type") == "ENTRYPOINT"]
    assert len(entrypoint_nodes) == 0, "ChatMessageTrigger workflows should NOT have an ENTRYPOINT node"

    # AND the workflow definition should reference the correct module
    definition = workflow_raw_data["definition"]
    assert definition == {
        "name": "SimpleChatWorkflow",
        "module": ["tests", "workflows", "chat_message_trigger_execution", "workflows", "simple_chat_workflow"],
    }

    # AND the output variables should include response and chat_history
    output_variables = result["output_variables"]
    assert isinstance(output_variables, list)
    output_keys = {var["key"] for var in output_variables if isinstance(var, dict)}
    assert "response" in output_keys
    assert "chat_history" in output_keys

    # AND the state variables should include chat_history
    state_variables = result["state_variables"]
    assert isinstance(state_variables, list)
    state_keys = {var["key"] for var in state_variables if isinstance(var, dict)}
    assert "chat_history" in state_keys
