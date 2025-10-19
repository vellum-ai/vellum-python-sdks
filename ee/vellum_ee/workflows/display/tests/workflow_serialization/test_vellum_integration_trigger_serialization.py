"""Tests for VellumIntegrationTrigger serialization."""

from typing import cast

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

    result = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # Verify triggers field exists
    assert "triggers" in result
    triggers = cast(list, result["triggers"])
    assert isinstance(triggers, list)
    assert len(triggers) == 1

    trigger = cast(dict, triggers[0])
    assert trigger["type"] == "INTEGRATION"

    # Check that attributes are serialized
    assert "attributes" in trigger
    attributes = cast(list, trigger["attributes"])
    assert len(attributes) == 3

    attribute_names = {cast(dict, attr)["name"] for attr in attributes}
    assert attribute_names == {"message", "channel", "user"}

    # RED: These assertions should fail because we haven't implemented class_name and module_path yet
    assert "class_name" in trigger, "Trigger should include class_name for codegen"
    assert trigger["class_name"] == "SlackMessageTrigger"

    assert "module_path" in trigger, "Trigger should include module_path for codegen"
    # The module path should be a list of strings representing the module hierarchy
    module_path = trigger["module_path"]
    assert isinstance(module_path, list)
    assert all(isinstance(part, str) for part in module_path)
