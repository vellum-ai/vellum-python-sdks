"""Tests for VellumIntegrationTrigger serialization."""

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_trigger_vellum_integration.workflow import VellumIntegrationTriggerWorkflow


def test_serialize_vellum_integration_trigger_workflow():
    """VellumIntegrationTrigger workflow serializes with both exec_config and attributes array."""
    workflow_display = get_workflow_display(workflow_class=VellumIntegrationTriggerWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
        "triggers",
    }

    triggers = serialized_workflow["triggers"]
    assert len(triggers) == 1

    trigger = triggers[0]
    assert trigger["type"] == "VELLUM_INTEGRATION_TRIGGER"
    assert trigger["id"] == "472448ae-3bb0-4ca5-86f3-0a19c023b2f7"

    # VellumIntegrationTrigger should have BOTH exec_config AND attributes (like SlackTrigger)
    assert "exec_config" in trigger
    assert "attributes" in trigger

    # Validate exec_config structure
    exec_config = trigger["exec_config"]
    assert exec_config == {
        "provider": "COMPOSIO",
        "integration_name": "SLACK",
        "slug": "slack_new_message",
        "trigger_nano_id": "abc123def456",
        "attributes": {"channel": "C123456"},
    }

    # Validate attributes array structure (matches SlackTrigger pattern)
    attributes = trigger["attributes"]
    assert isinstance(attributes, list)
    assert len(attributes) == 2  # message and channel

    # Verify attributes have correct structure
    attribute_names = {attr["name"] for attr in attributes}
    assert attribute_names == {"message", "channel"}

    for attr in attributes:
        assert "id" in attr
        assert "name" in attr
        assert "type" in attr
        assert "value" in attr
        assert attr["value"] is None
        # Dynamic attributes use types=(object,) which maps to JSON type
        assert attr["type"] == "JSON"


def test_vellum_integration_trigger_id_consistency():
    """
    Regression test: Ensure trigger IDs match between trigger definition and attribute references.

    This test validates that when a node references trigger attributes, the trigger_id
    in the output value matches the trigger's id in the triggers array. This prevents
    bugs where trigger IDs are generated inconsistently.
    """
    workflow_display = get_workflow_display(workflow_class=VellumIntegrationTriggerWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    triggers = serialized_workflow["triggers"]
    assert len(triggers) == 1
    trigger_id = triggers[0]["id"]

    # Find the ProcessMessageNode in the serialized nodes
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    nodes = workflow_raw_data["nodes"]

    process_node = next(
        node for node in nodes if node.get("type") == "GENERIC" and node.get("label") == "Process Message Node"
    )

    # Verify the node has outputs that reference the trigger
    assert "outputs" in process_node
    outputs = process_node["outputs"]

    # Check that all trigger attribute references use the correct trigger_id
    for output in outputs:
        if output.get("value", {}).get("type") == "TRIGGER_ATTRIBUTE":
            output_trigger_id = output["value"]["trigger_id"]
            assert output_trigger_id == trigger_id, (
                f"Trigger ID mismatch: trigger definition has ID {trigger_id}, "
                f"but output '{output['name']}' references trigger ID {output_trigger_id}. "
                "This indicates inconsistent trigger ID generation."
            )


def test_vellum_integration_trigger_multiple_attributes():
    """VellumIntegrationTrigger with multiple attribute references serializes correctly."""
    workflow_display = get_workflow_display(workflow_class=VellumIntegrationTriggerWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    nodes = workflow_raw_data["nodes"]

    process_node = next(
        node for node in nodes if node.get("type") == "GENERIC" and node.get("label") == "Process Message Node"
    )

    outputs = process_node["outputs"]
    assert isinstance(outputs, list), "outputs should be a list"
    assert len(outputs) == 2

    # Verify both outputs reference trigger attributes
    processed_message_output = next(o for o in outputs if isinstance(o, dict) and o.get("name") == "processed_message")
    assert isinstance(processed_message_output, dict), "output should be a dict"
    assert isinstance(processed_message_output.get("value"), dict), "value should be a dict"
    assert processed_message_output["value"]["type"] == "TRIGGER_ATTRIBUTE"
    assert "attribute_id" in processed_message_output["value"]

    channel_output = next(o for o in outputs if isinstance(o, dict) and o.get("name") == "channel")
    assert isinstance(channel_output, dict), "output should be a dict"
    assert isinstance(channel_output.get("value"), dict), "value should be a dict"
    assert channel_output["value"]["type"] == "TRIGGER_ATTRIBUTE"
    assert "attribute_id" in channel_output["value"]


def test_vellum_integration_trigger_without_attributes():
    """VellumIntegrationTrigger without accessed attributes serializes with empty attributes array."""
    from vellum.workflows import BaseWorkflow
    from vellum.workflows.inputs.base import BaseInputs
    from vellum.workflows.nodes.bases.base import BaseNode
    from vellum.workflows.state.base import BaseState
    from vellum.workflows.triggers.vellum_integration import VellumIntegrationTrigger

    # Create trigger without attributes parameter
    GitHubPush = VellumIntegrationTrigger.for_trigger(
        provider="COMPOSIO",
        integration_name="GITHUB",
        slug="github_push_event",
        trigger_nano_id="xyz789ghi012",
    )

    class SimpleNode(BaseNode):
        pass

    class SimpleWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = GitHubPush >> SimpleNode

    workflow_display = get_workflow_display(workflow_class=SimpleWorkflow)
    result = workflow_display.serialize()

    triggers = result["triggers"]
    assert isinstance(triggers, list), "triggers should be a list"
    assert len(triggers) == 1

    trigger = triggers[0]
    assert isinstance(trigger, dict), "trigger should be a dict"
    assert trigger["type"] == "VELLUM_INTEGRATION_TRIGGER"

    # Validate exec_config
    exec_config = trigger["exec_config"]
    assert isinstance(exec_config, dict), "exec_config should be a dict"
    assert exec_config["attributes"] == {}  # No filter attributes
    assert exec_config["provider"] == "COMPOSIO"
    assert exec_config["integration_name"] == "GITHUB"
    assert exec_config["slug"] == "github_push_event"
    assert exec_config["trigger_nano_id"] == "xyz789ghi012"

    # Validate attributes array is empty (no attributes accessed in workflow)
    assert "attributes" in trigger
    assert trigger["attributes"] == []
