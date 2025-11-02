"""Tests for IntegrationTrigger serialization."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_vellum_integration_trigger_serialization():
    """IntegrationTrigger subclass serializes with class name and module path."""

    # Create a custom IntegrationTrigger subclass
    class SlackMessageTrigger(IntegrationTrigger):
        """Custom Slack message trigger."""

        message: str
        channel: str
        user: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "SLACK"
            slug = "slack_new_message"

    class ProcessNode(BaseNode):
        """Node that processes the trigger."""

        class Outputs(BaseNode.Outputs):
            result = SlackMessageTrigger.message

        def run(self) -> Outputs:
            return self.Outputs()

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = SlackMessageTrigger >> ProcessNode

    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # Verify triggers field exists
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1

    trigger = triggers[0]
    assert isinstance(trigger, dict)
    assert trigger["type"] == "INTEGRATION"

    # Check that attributes are serialized
    assert "attributes" in trigger
    attributes = trigger["attributes"]
    assert isinstance(attributes, list)
    assert len(attributes) == 3

    attribute_names = {attr["name"] for attr in attributes if isinstance(attr, dict)}
    assert attribute_names == {"message", "channel", "user"}

    # RED: These assertions should fail because we haven't implemented class_name and module_path yet
    assert "class_name" in trigger, "Trigger should include class_name for codegen"
    assert trigger["class_name"] == "SlackMessageTrigger"

    assert "module_path" in trigger, "Trigger should include module_path for codegen"
    # The module path should be a list of strings representing the module hierarchy
    module_path = trigger["module_path"]
    assert isinstance(module_path, list)
    assert all(isinstance(part, str) for part in module_path)


def test_vellum_integration_trigger_id_consistency():
    """Validates trigger and attribute IDs match between definitions and references."""

    class SlackMessageTrigger(IntegrationTrigger):
        message: str
        channel: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "SLACK"
            slug = "slack_new_message"

    class ProcessNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            msg_output = SlackMessageTrigger.message
            channel_output = SlackMessageTrigger.channel

        def run(self) -> Outputs:
            return self.Outputs()

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = SlackMessageTrigger >> ProcessNode

    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # Get trigger definition IDs
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    trigger = triggers[0]
    assert isinstance(trigger, dict)
    trigger_id = trigger["id"]
    trigger_attributes = trigger["attributes"]
    assert isinstance(trigger_attributes, list)
    trigger_attrs = {attr["name"]: attr["id"] for attr in trigger_attributes if isinstance(attr, dict)}

    # Find node with trigger attribute references
    workflow_raw_data = result["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)
    nodes = workflow_raw_data["nodes"]
    assert isinstance(nodes, list)
    process_node = next(
        (
            n
            for n in nodes
            if isinstance(n, dict)
            and isinstance(n.get("outputs"), list)
            and any(
                isinstance(o, dict)
                and isinstance(o.get("value"), dict)
                and o.get("value", {}).get("type") == "TRIGGER_ATTRIBUTE"
                for o in n.get("outputs", [])
            )
        ),
        None,
    )
    assert process_node, "No node found with trigger attribute references"

    # Validate all trigger attribute references have matching IDs
    attr_mapping = {"msg_output": "message", "channel_output": "channel"}
    outputs = process_node["outputs"]
    assert isinstance(outputs, list)
    for output in outputs:
        if not isinstance(output, dict):
            continue
        value = output.get("value", {})
        if not isinstance(value, dict):
            continue
        if value.get("type") == "TRIGGER_ATTRIBUTE":
            assert value["trigger_id"] == trigger_id, "Trigger ID mismatch"

            output_name = output["name"]
            expected_attr = attr_mapping[output_name]
            expected_id = trigger_attrs[expected_attr]
            assert value["attribute_id"] == expected_id, f"Attribute ID mismatch for {expected_attr}"


def test_trigger_module_paths_are_canonical():
    """Validates trigger module_path and class_name for consistent codegen."""

    class TestSlackTrigger(IntegrationTrigger):
        message: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "SLACK"
            slug = "test_slack_trigger"

    class SimpleNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result = TestSlackTrigger.message

        def run(self) -> Outputs:
            return self.Outputs()

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = TestSlackTrigger >> SimpleNode

    result = get_workflow_display(workflow_class=TestWorkflow).serialize()

    triggers = result["triggers"]
    assert isinstance(triggers, list)
    trigger = triggers[0]
    assert isinstance(trigger, dict)
    assert trigger["type"] == "INTEGRATION"

    module_path = trigger["module_path"]
    assert isinstance(module_path, list)
    assert all(isinstance(part, str) for part in module_path)
    assert module_path == __name__.split(".")

    assert trigger["class_name"] == "TestSlackTrigger"


def test_integration_trigger_no_entrypoint_node():
    """IntegrationTrigger workflows now create ENTRYPOINT nodes and route edges through them."""

    class SlackMessageTrigger(IntegrationTrigger):
        message: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "SLACK"
            slug = "slack_message"

    class ProcessNode(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = SlackMessageTrigger >> ProcessNode

    result = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # Get trigger ID
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1
    trigger = triggers[0]
    assert isinstance(trigger, dict)
    trigger_id = trigger["id"]

    # Verify trigger has source_handle_id matching trigger_id
    assert "source_handle_id" in trigger, "Trigger should have source_handle_id"
    assert trigger["source_handle_id"] == trigger_id, "source_handle_id should match trigger_id"

    # Verify ENTRYPOINT node exists
    workflow_raw_data = result["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)
    nodes = workflow_raw_data["nodes"]
    assert isinstance(nodes, list)
    entrypoint_nodes = [n for n in nodes if isinstance(n, dict) and n.get("type") == "ENTRYPOINT"]
    assert len(entrypoint_nodes) == 1, "IntegrationTrigger workflows should have an ENTRYPOINT node"

    entrypoint_node = entrypoint_nodes[0]
    assert isinstance(entrypoint_node, dict)
    entrypoint_node_id = entrypoint_node["id"]

    edges = workflow_raw_data["edges"]
    assert isinstance(edges, list)
    entrypoint_edges = [e for e in edges if isinstance(e, dict) and e.get("source_node_id") == entrypoint_node_id]
    assert len(entrypoint_edges) == 0

    # Verify edges use trigger ID as sourceNodeId (not ENTRYPOINT)
    trigger_edges = [e for e in edges if isinstance(e, dict) and e.get("source_node_id") == trigger_id]
    assert len(trigger_edges) > 0, "Should have edges from trigger ID"

    # Verify the edge connects trigger to first node
    # ProcessNode should be the only non-terminal, non-entrypoint node
    process_nodes = [n for n in nodes if isinstance(n, dict) and n.get("type") not in ("TERMINAL", "ENTRYPOINT")]
    assert len(process_nodes) > 0, "Should have at least one process node"
    process_node = process_nodes[0]
    assert isinstance(process_node, dict)
    process_node_id = process_node["id"]

    trigger_to_process_edge = next(
        (e for e in trigger_edges if isinstance(e, dict) and e.get("target_node_id") == process_node_id),
        None,
    )
    assert trigger_to_process_edge is not None, "Should have edge from trigger to ProcessNode"
    assert isinstance(trigger_to_process_edge, dict)
    assert trigger_to_process_edge["source_node_id"] == trigger_id
    assert trigger_to_process_edge["target_node_id"] == process_node_id
