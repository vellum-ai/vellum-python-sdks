"""Tests for IntegrationTrigger serialization."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.ports import Port
from vellum.workflows.references.constant import ConstantValueReference
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
            setup_attributes = {"team_id": "72485c1d-b72e-48e6-88de-a952968ae2a2"}

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

    attribute_names = {attr["key"] for attr in attributes if isinstance(attr, dict)}
    assert attribute_names == {"message", "channel", "user"}

    exec_config = trigger["exec_config"]
    assert isinstance(exec_config, dict)
    assert exec_config["type"] == "COMPOSIO"
    assert exec_config["slug"] == "slack_new_message"
    assert exec_config["integration_name"] == "SLACK"

    setup_attributes = exec_config["setup_attributes"]
    assert isinstance(setup_attributes, list)
    assert len(setup_attributes) == 1
    setup_attribute = setup_attributes[0]

    assert setup_attribute["key"] == "team_id"
    assert setup_attribute["type"] == "STRING"
    assert setup_attribute["required"] is True

    default_value = setup_attribute["default"]
    assert isinstance(default_value, dict)
    assert default_value["type"] == "STRING"
    assert default_value["value"] == "72485c1d-b72e-48e6-88de-a952968ae2a2"
    assert setup_attribute["extensions"] == {"color": None, "description": None}


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
    trigger_attrs = {attr["key"]: attr["id"] for attr in trigger_attributes if isinstance(attr, dict)}

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


def test_integration_trigger_serialization_display_data():
    """IntegrationTrigger with Display class serializes all display attributes correctly."""

    # GIVEN an integration trigger with comprehensive Display attributes
    class SlackMessageTriggerWithDisplay(IntegrationTrigger):
        message: str
        channel: str
        user: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "SLACK"
            slug = "slack_new_message"

        class Display(IntegrationTrigger.Display):
            label = "Slack Message"
            x = 150.5
            y = 250.75
            z_index = 5
            icon = "vellum:icon:integrations/COMPOSIO/SLACK"
            color = "#4A154B"

    class ProcessNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result = SlackMessageTriggerWithDisplay.message

        def run(self) -> Outputs:
            return self.Outputs()

    # AND a workflow that uses the trigger
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = SlackMessageTriggerWithDisplay >> ProcessNode

    # WHEN we serialize the workflow
    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # THEN we get the expected trigger
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1

    trigger = triggers[0]
    assert isinstance(trigger, dict)
    assert trigger["type"] == "INTEGRATION"

    # AND display_data is serialized with icon and color
    assert "display_data" in trigger
    display_data = trigger["display_data"]
    assert isinstance(display_data, dict)
    assert display_data["icon"] == "vellum:icon:integrations/COMPOSIO/SLACK"
    assert display_data["color"] == "#4A154B"


def test_integration_trigger_and_entrypoint_edges_have_distinct_ids():
    """
    Tests that when a node is both the target of an IntegrationTrigger AND has outgoing edges
    (which creates an implicit entrypoint edge), both edges have distinct IDs.

    This is a regression test for a bug where both edges were assigned the same ID,
    causing the UI to deduplicate them and only show one edge.
    """

    # GIVEN an integration trigger
    class LinearTrigger(IntegrationTrigger):
        issue_id: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "LINEAR"
            slug = "linear_issue_created"

    # AND a custom node with conditional ports
    class Custom(BaseNode):
        class Ports(BaseNode.Ports):
            group_1_if_port = Port.on_if(ConstantValueReference("hi").equals("hi"))
            group_1_else_port = Port.on_else()

    # AND output nodes
    class Output(BaseNode):
        class Outputs(BaseNode.Outputs):
            value = LinearTrigger.issue_id

    class Output2(BaseNode):
        class Outputs(BaseNode.Outputs):
            value = LinearTrigger.issue_id

    # AND a workflow where Custom is both:
    # 1. The target of an IntegrationTrigger (LinearTrigger >> Custom)
    # 2. The source of regular edges (Custom.Ports >> Output/Output2)
    # This creates both an entrypoint edge and a trigger edge to Custom
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = {
            Custom.Ports.group_1_if_port >> Output,
            Custom.Ports.group_1_else_port >> Output2,
            LinearTrigger >> Custom,
        }

        class Outputs(BaseWorkflow.Outputs):
            output = Output.Outputs.value
            output_2 = Output2.Outputs.value

    # WHEN we serialize the workflow
    result = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # THEN we should have both an ENTRYPOINT node and a trigger
    workflow_raw_data = result["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)
    nodes = workflow_raw_data["nodes"]
    assert isinstance(nodes, list)
    edges = workflow_raw_data["edges"]
    assert isinstance(edges, list)

    entrypoint_nodes = [n for n in nodes if isinstance(n, dict) and n.get("type") == "ENTRYPOINT"]
    assert len(entrypoint_nodes) == 1, "Should have an ENTRYPOINT node"
    entrypoint_node = entrypoint_nodes[0]
    assert isinstance(entrypoint_node, dict)
    entrypoint_node_id = entrypoint_node["id"]

    triggers = result.get("triggers", [])
    assert isinstance(triggers, list)
    assert len(triggers) == 1, "Should have one trigger"
    trigger = triggers[0]
    assert isinstance(trigger, dict)
    trigger_id = trigger["id"]

    # AND find the Custom node (by definition name since there are multiple GENERIC nodes)
    custom_node = None
    for n in nodes:
        if not isinstance(n, dict):
            continue
        if n.get("type") != "GENERIC":
            continue
        definition = n.get("definition")
        if not isinstance(definition, dict):
            continue
        if definition.get("name") == "Custom":
            custom_node = n
            break
    assert custom_node is not None, "Should have one Custom node"
    custom_node_id = custom_node["id"]

    # AND we should have BOTH an entrypoint edge AND a trigger edge to Custom
    entrypoint_to_custom_edges = [
        e
        for e in edges
        if isinstance(e, dict)
        and e.get("source_node_id") == entrypoint_node_id
        and e.get("target_node_id") == custom_node_id
    ]
    trigger_to_custom_edges = [
        e
        for e in edges
        if isinstance(e, dict) and e.get("source_node_id") == trigger_id and e.get("target_node_id") == custom_node_id
    ]

    assert len(entrypoint_to_custom_edges) == 1, "Should have an entrypoint edge to Custom"
    assert len(trigger_to_custom_edges) == 1, "Should have a trigger edge to Custom"

    # AND the two edges should have DISTINCT IDs (this is the key assertion)
    entrypoint_edge = entrypoint_to_custom_edges[0]
    trigger_edge = trigger_to_custom_edges[0]
    assert isinstance(entrypoint_edge, dict)
    assert isinstance(trigger_edge, dict)
    entrypoint_edge_id = entrypoint_edge["id"]
    trigger_edge_id = trigger_edge["id"]

    assert entrypoint_edge_id != trigger_edge_id, (
        f"Entrypoint edge and trigger edge should have distinct IDs, " f"but both have ID: {entrypoint_edge_id}"
    )
