"""Tests for VellumIntegrationTrigger serialization."""

from typing import Any, cast

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.vellum_integration import VellumIntegrationTrigger
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_vellum_integration_trigger_serialization():
    """VellumIntegrationTrigger subclass serializes with class name and module path."""

    # Create a custom VellumIntegrationTrigger subclass
    class SlackMessageTrigger(VellumIntegrationTrigger):
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
    assert trigger["type"] == "INTEGRATION"

    # Check that attributes are serialized
    assert "attributes" in trigger
    attributes = trigger["attributes"]
    assert len(attributes) == 3

    attribute_names = {attr["name"] for attr in attributes}
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

    class SlackMessageTrigger(VellumIntegrationTrigger):
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
    trigger = result["triggers"][0]
    trigger_id = trigger["id"]
    trigger_attrs = {attr["name"]: attr["id"] for attr in trigger["attributes"]}

    # Find node with trigger attribute references
    nodes = result["workflow_raw_data"]["nodes"]
    process_node = next(
        (n for n in nodes if any(o.get("value", {}).get("type") == "TRIGGER_ATTRIBUTE" for o in n.get("outputs", []))),
        None,
    )
    assert process_node, "No node found with trigger attribute references"

    # Validate all trigger attribute references have matching IDs
    attr_mapping = {"msg_output": "message", "channel_output": "channel"}
    for output in process_node["outputs"]:
        value = output.get("value", {})
        if value.get("type") == "TRIGGER_ATTRIBUTE":
            assert value["trigger_id"] == trigger_id, "Trigger ID mismatch"

            expected_attr = attr_mapping[output["name"]]
            expected_id = trigger_attrs[expected_attr]
            assert value["attribute_id"] == expected_id, f"Attribute ID mismatch for {expected_attr}"


def test_vellum_integration_trigger_entrypoint_id_consistency():
    """VellumIntegrationTrigger ID matches entrypoint node ID for proper linkage."""

    class SlackMessageTrigger(VellumIntegrationTrigger):
        """Custom Slack message trigger."""

        message: str

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

    # Get trigger ID
    triggers = result["triggers"]
    assert len(triggers) == 1
    trigger_id = triggers[0]["id"]

    # Get entrypoint node ID
    nodes = result["workflow_raw_data"]["nodes"]
    entrypoint_nodes = [n for n in nodes if n["type"] == "ENTRYPOINT"]
    assert len(entrypoint_nodes) == 1
    entrypoint_id = entrypoint_nodes[0]["id"]

    # Verify IDs match - this is critical for frontend to understand trigger-entrypoint relationship
    assert trigger_id == entrypoint_id, (
        f"VellumIntegrationTrigger ID ({trigger_id}) must match entrypoint node ID ({entrypoint_id}) "
        "to maintain trigger-entrypoint linkage"
    )


def test_trigger_module_paths_are_canonical():
    """Validates trigger module_path and class_name for consistent codegen."""

    class TestSlackTrigger(VellumIntegrationTrigger):
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

    triggers = cast(list[Any], result["triggers"])
    trigger = cast(dict[str, Any], triggers[0])
    assert trigger["type"] == "INTEGRATION"

    module_path = cast(list[Any], trigger["module_path"])
    assert isinstance(module_path, list)
    assert all(isinstance(part, str) for part in module_path)
    assert module_path == __name__.split(".")

    assert trigger["class_name"] == "TestSlackTrigger"
