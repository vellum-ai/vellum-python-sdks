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
    """
    Regression test: Ensure trigger IDs remain consistent across references.

    This test validates that trigger IDs generated in the trigger definition
    match the trigger IDs referenced in node outputs. This prevents bugs where
    IDs become inconsistent due to changes in hash formulas or import paths.

    Context: PR #2747 fixed a bug where trigger IDs were inconsistent because
    __module__ was included in the hash formula, causing IDs to vary based on
    import paths.
    """

    # Create a custom VellumIntegrationTrigger subclass
    class SlackMessageTrigger(VellumIntegrationTrigger):
        """Custom Slack message trigger for testing ID consistency."""

        message: str
        channel: str
        user: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "SLACK"
            slug = "slack_new_message"

    class ProcessNode(BaseNode):
        """Node that references trigger attributes."""

        class Outputs(BaseNode.Outputs):
            # Reference trigger attributes - these should generate consistent IDs
            msg_output = SlackMessageTrigger.message
            channel_output = SlackMessageTrigger.channel
            user_output = SlackMessageTrigger.user

        def run(self) -> Outputs:
            return self.Outputs()

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = SlackMessageTrigger >> ProcessNode

    # Serialize the workflow
    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # Extract trigger definition
    triggers = result["triggers"]
    assert len(triggers) == 1
    trigger = triggers[0]
    trigger_id = trigger["id"]

    # Extract trigger attributes and their IDs
    trigger_attributes = {attr["name"]: attr["id"] for attr in trigger["attributes"]}

    # Find the ProcessNode in the workflow
    nodes = result["workflow_raw_data"]["nodes"]

    # Find ProcessNode - it might have different type or label in the serialized form
    process_node = None
    for node in nodes:
        if node.get("label") == "ProcessNode" or (node.get("data", {}).get("label") == "ProcessNode"):
            process_node = node
            break

    # If we can't find by label, look for a node with outputs that reference triggers
    if not process_node:
        for node in nodes:
            if node.get("outputs"):
                # Check if any output references a trigger
                for output in node.get("outputs", []):
                    if output.get("value", {}).get("type") == "TRIGGER_ATTRIBUTE":
                        process_node = node
                        break
                if process_node:
                    break

    assert process_node is not None, f"Could not find ProcessNode in nodes: {nodes}"

    # Check that node outputs reference the correct trigger and attribute IDs
    outputs = process_node["outputs"]

    # Each output should reference a trigger attribute
    for output in outputs:
        if "value" in output and isinstance(output["value"], dict):
            value = output["value"]

            # If this is a trigger attribute reference, validate IDs match
            if value.get("type") == "TRIGGER_ATTRIBUTE":
                # The trigger ID in the reference should match the trigger definition
                assert value["trigger_id"] == trigger_id, (
                    f"Trigger ID mismatch: reference has {value['trigger_id']}, "
                    f"but trigger definition has {trigger_id}. "
                    "This indicates an ID generation inconsistency."
                )

                # The attribute ID should match the corresponding attribute in the trigger
                attribute_id = value["attribute_id"]
                output_name = output["name"]

                # Map output names to expected attribute names
                attribute_mapping = {
                    "msg_output": "message",
                    "channel_output": "channel",
                    "user_output": "user",
                }

                if output_name in attribute_mapping:
                    expected_attr_name = attribute_mapping[output_name]
                    expected_attr_id = trigger_attributes[expected_attr_name]
                    assert attribute_id == expected_attr_id, (
                        f"Attribute ID mismatch for {output_name}: "
                        f"reference has {attribute_id}, "
                        f"but trigger attribute '{expected_attr_name}' has {expected_attr_id}. "
                        "This indicates an attribute ID generation inconsistency."
                    )


def test_trigger_module_paths_are_canonical():
    """
    Ensure triggers use canonical import paths for consistent codegen.

    Module paths are used to generate import statements in TypeScript.
    They should be consistent regardless of how the trigger is imported in Python.

    This test validates that the module_path field in serialized triggers
    matches the expected canonical path for known triggers.
    """

    # Create a custom VellumIntegrationTrigger subclass defined inline
    class TestSlackTrigger(VellumIntegrationTrigger):
        """Test Slack trigger for module path validation."""

        message: str
        channel: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "SLACK"
            slug = "test_slack_trigger"

    class SimpleNode(BaseNode):
        """Simple node to complete the workflow."""

        class Outputs(BaseNode.Outputs):
            result = TestSlackTrigger.message

        def run(self) -> Outputs:
            return self.Outputs()

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = TestSlackTrigger >> SimpleNode

    # Serialize the workflow
    result = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # Get the trigger and its module path
    triggers = cast(list[Any], result["triggers"])
    trigger = cast(dict[str, Any], triggers[0])
    assert trigger["type"] == "INTEGRATION"

    module_path = cast(list[Any], trigger["module_path"])
    assert isinstance(module_path, list), "module_path should be a list of strings"
    assert all(isinstance(part, str) for part in module_path), "All module_path parts should be strings"

    # The module path should reflect where the class is defined
    # Since TestSlackTrigger is defined inline in this test function,
    # its module should be this test module
    expected_module_parts = __name__.split(".")

    assert module_path == expected_module_parts, (
        f"Module path {module_path} doesn't match expected {expected_module_parts}. "
        "This could cause inconsistent imports in generated TypeScript code."
    )

    # Verify the class_name is correct
    class_name = cast(str, trigger["class_name"])
    assert class_name == "TestSlackTrigger"

    # Additional validation: If we had triggers imported from fixtures,
    # we'd want to ensure they always use the canonical fixture path
    # For example:
    # from tests.fixtures.triggers.slack import SlackTrigger
    # should always produce ["tests", "fixtures", "triggers", "slack"]
    # regardless of relative vs absolute imports
