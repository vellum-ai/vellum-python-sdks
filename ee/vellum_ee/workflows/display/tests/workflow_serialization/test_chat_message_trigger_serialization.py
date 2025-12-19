"""Tests for ChatMessageTrigger serialization."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.chat_message import ChatMessageTrigger
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.editor import NodeDisplayComment
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.chat_message_trigger_execution.workflows.simple_chat_workflow import SimpleChatWorkflow


def test_chat_message_trigger_serialization():
    """ChatMessageTrigger serializes with type CHAT_MESSAGE and message attribute."""

    # GIVEN a ChatMessageTrigger subclass
    class MyChatMessageTrigger(ChatMessageTrigger):
        pass

    class ProcessNode(BaseNode):
        pass

    # AND a workflow that uses the trigger
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = MyChatMessageTrigger >> ProcessNode

    # WHEN we serialize the workflow
    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # THEN we get the expected trigger
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1

    trigger = triggers[0]
    assert isinstance(trigger, dict)

    # AND the trigger type is CHAT_MESSAGE
    assert trigger["type"] == "CHAT_MESSAGE"

    # AND attributes are serialized (message from ChatMessageTrigger)
    assert "attributes" in trigger
    attributes = trigger["attributes"]
    assert isinstance(attributes, list)
    assert len(attributes) == 1

    attribute_keys = {attr["key"] for attr in attributes if isinstance(attr, dict)}
    assert attribute_keys == {"message"}


def test_chat_message_trigger_serialization_without_metadata_json():
    """ChatMessageTrigger uses default hash-based __id__ when no metadata.json is available."""

    # GIVEN a ChatMessageTrigger defined without metadata.json
    class SimpleChatTrigger(ChatMessageTrigger):
        pass

    class ProcessNode(BaseNode):
        pass

    # AND a workflow that uses the trigger
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = SimpleChatTrigger >> ProcessNode

    # WHEN we serialize the workflow without metadata.json
    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # THEN we get the expected trigger
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1

    trigger = triggers[0]
    assert isinstance(trigger, dict)
    assert trigger["type"] == "CHAT_MESSAGE"

    # AND the id is the trigger class's default __id__ (hash-based)
    expected_module_path = (
        f"{__name__}.test_chat_message_trigger_serialization_without_metadata_json.<locals>.SimpleChatTrigger"
    )
    expected_default_id = str(uuid4_from_hash(expected_module_path))
    assert trigger["id"] == expected_default_id


def test_chat_message_trigger_serialization_display_data():
    """ChatMessageTrigger with Display class serializes all display attributes correctly."""

    # GIVEN a ChatMessageTrigger with comprehensive Display attributes
    class ChatTriggerWithDisplay(ChatMessageTrigger):
        class Display(ChatMessageTrigger.Display):
            label = "Chat Input"
            x = 120.5
            y = 180.75
            z_index = 4
            icon = "vellum:icon:message"
            color = "#3B82F6"

    class ProcessNode(BaseNode):
        pass

    # AND a workflow that uses the trigger
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = ChatTriggerWithDisplay >> ProcessNode

    # WHEN we serialize the workflow
    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # THEN we get the expected trigger
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1

    trigger = triggers[0]
    assert isinstance(trigger, dict)
    assert trigger["type"] == "CHAT_MESSAGE"

    # AND display_data is serialized with icon and color
    assert "display_data" in trigger
    display_data = trigger["display_data"]
    assert isinstance(display_data, dict)
    assert display_data["icon"] == "vellum:icon:message"
    assert display_data["color"] == "#3B82F6"
    assert display_data["label"] == "Chat Input"
    assert display_data["position"] == {"x": 120.5, "y": 180.75}
    assert display_data["z_index"] == 4


def test_chat_message_trigger_serialization_with_comment():
    """ChatMessageTrigger with Display comment serializes correctly."""

    # GIVEN a ChatMessageTrigger with Display comment
    class ChatTriggerWithComment(ChatMessageTrigger):
        class Display(ChatMessageTrigger.Display):
            label = "Chat Trigger"
            x = 100.0
            y = 200.0
            z_index = 2
            icon = "vellum:icon:message"
            color = "#10B981"
            comment = NodeDisplayComment(value="This is a chat message trigger", expanded=True)

    class ProcessNode(BaseNode):
        pass

    # AND a workflow that uses the trigger
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = ChatTriggerWithComment >> ProcessNode

    # WHEN we serialize the workflow
    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # THEN we get the expected trigger
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1

    trigger = triggers[0]
    assert isinstance(trigger, dict)
    assert trigger["type"] == "CHAT_MESSAGE"

    # AND display_data includes the comment
    assert "display_data" in trigger
    display_data = trigger["display_data"]
    assert isinstance(display_data, dict)
    assert "comment" in display_data
    assert display_data["comment"] == {
        "value": "This is a chat message trigger",
        "expanded": True,
    }


def test_chat_message_trigger_no_entrypoint_node():
    """ChatMessageTrigger-only workflows should NOT have an ENTRYPOINT node."""

    # GIVEN a ChatMessageTrigger workflow where all branches are sourced from the trigger
    class MyChatTrigger(ChatMessageTrigger):
        pass

    class ProcessNode(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = MyChatTrigger >> ProcessNode

    # WHEN we serialize the workflow
    result = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # THEN the trigger should be serialized
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1
    trigger = triggers[0]
    assert isinstance(trigger, dict)
    trigger_id = trigger["id"]

    # AND there should be NO ENTRYPOINT node (all branches are trigger-sourced)
    workflow_raw_data = result["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)
    nodes = workflow_raw_data["nodes"]
    assert isinstance(nodes, list)
    entrypoint_nodes = [n for n in nodes if isinstance(n, dict) and n.get("type") == "ENTRYPOINT"]
    assert len(entrypoint_nodes) == 0, "ChatMessageTrigger-only workflows should NOT have an ENTRYPOINT node"

    # AND edges should use trigger ID as source_node_id
    edges = workflow_raw_data["edges"]
    assert isinstance(edges, list)
    trigger_edges = [e for e in edges if isinstance(e, dict) and e.get("source_node_id") == trigger_id]
    assert len(trigger_edges) > 0, "Should have edges from trigger ID"


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
