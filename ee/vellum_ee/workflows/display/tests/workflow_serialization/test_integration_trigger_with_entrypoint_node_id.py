"""Tests for IntegrationTrigger with explicit entrypoint_node_id serialization."""

from uuid import uuid4

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum_ee.workflows.display.base import EdgeDisplay, EntrypointDisplay, WorkflowMetaDisplay
from vellum_ee.workflows.display.editor.types import NodeDisplayData
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_integration_trigger_with_explicit_entrypoint_node_id():
    """
    Tests that a workflow with an IntegrationTrigger and explicit entrypoint_node_id
    creates an ENTRYPOINT node using the explicit ID (not the trigger's ID).
    """

    class SlackMessageTrigger(IntegrationTrigger):
        message: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "SLACK"
            slug = "slack_message"

    class ProcessNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result = SlackMessageTrigger.message

        def run(self) -> Outputs:
            return self.Outputs()

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = SlackMessageTrigger >> ProcessNode

    explicit_entrypoint_node_id = uuid4()
    explicit_entrypoint_source_handle_id = uuid4()

    class TestWorkflowDisplay(BaseWorkflowDisplay[TestWorkflow]):
        workflow_display = WorkflowMetaDisplay(
            entrypoint_node_id=explicit_entrypoint_node_id,
            entrypoint_node_source_handle_id=explicit_entrypoint_source_handle_id,
            entrypoint_node_display=NodeDisplayData(),
        )
        entrypoint_displays = {
            ProcessNode: EntrypointDisplay(
                id=uuid4(),
                edge_display=EdgeDisplay(id=uuid4()),
            )
        }

    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    assert "workflow_raw_data" in result
    workflow_raw_data = result["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)

    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1
    trigger = triggers[0]
    assert isinstance(trigger, dict)
    trigger_id = trigger["id"]

    nodes = workflow_raw_data["nodes"]
    assert isinstance(nodes, list)

    entrypoint_nodes = [n for n in nodes if isinstance(n, dict) and n.get("type") == "ENTRYPOINT"]

    assert (
        len(entrypoint_nodes) == 1
    ), "IntegrationTrigger workflows with explicit entrypoint_node_id should create an ENTRYPOINT node"

    entrypoint_node = entrypoint_nodes[0]
    assert isinstance(entrypoint_node, dict)
    entrypoint_node_id = entrypoint_node["id"]

    assert entrypoint_node_id == str(explicit_entrypoint_node_id), (
        f"Entrypoint node ID should be {explicit_entrypoint_node_id} from workflow_display, "
        f"not {trigger_id} from trigger"
    )

    assert entrypoint_node_id != trigger_id, "Entrypoint node should not use the trigger's ID"
