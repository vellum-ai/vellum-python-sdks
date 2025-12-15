"""Tests for multiple triggers pointing to the same node."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum.workflows.triggers.manual import ManualTrigger
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_manual_and_slack_trigger_same_node():
    """
    Tests that when Manual and Slack triggers point to the same node,
    we have edges for both triggers.
    """

    class MyManualTrigger(ManualTrigger):
        pass

    class SlackMessageTrigger(IntegrationTrigger):
        message: str
        channel: str

        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"

    class ProcessNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

        def run(self) -> Outputs:
            return self.Outputs(result="processed")

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = {
            MyManualTrigger >> ProcessNode,
            SlackMessageTrigger >> ProcessNode,
        }

    result = get_workflow_display(workflow_class=TestWorkflow).serialize()

    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 2

    manual_trigger = next((t for t in triggers if isinstance(t, dict) and t.get("type") == "MANUAL"), None)
    assert manual_trigger is not None, "Should have a Manual trigger"
    assert isinstance(manual_trigger, dict)
    manual_trigger_id = manual_trigger["id"]

    slack_trigger = next((t for t in triggers if isinstance(t, dict) and t.get("type") == "INTEGRATION"), None)
    assert slack_trigger is not None, "Should have a Slack trigger"
    assert isinstance(slack_trigger, dict)
    slack_trigger_id = slack_trigger["id"]

    workflow_raw_data = result["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)
    edges = workflow_raw_data["edges"]
    assert isinstance(edges, list)

    nodes = workflow_raw_data["nodes"]
    assert isinstance(nodes, list)
    process_nodes = [n for n in nodes if isinstance(n, dict) and n.get("type") not in ("TERMINAL", "ENTRYPOINT")]
    assert len(process_nodes) > 0, "Should have at least one process node"
    process_node = process_nodes[0]
    process_node_id = process_node["id"]

    manual_edge = next(
        (
            e
            for e in edges
            if isinstance(e, dict)
            and e.get("source_node_id") == manual_trigger_id
            and e.get("target_node_id") == process_node_id
        ),
        None,
    )
    assert manual_edge is not None, (
        f"Should have edge from Manual trigger ({manual_trigger_id}) " f"to ProcessNode ({process_node_id})"
    )

    slack_edge = next(
        (
            e
            for e in edges
            if isinstance(e, dict)
            and e.get("source_node_id") == slack_trigger_id
            and e.get("target_node_id") == process_node_id
        ),
        None,
    )
    assert slack_edge is not None, (
        f"Should have edge from Slack trigger ({slack_trigger_id}) " f"to ProcessNode ({process_node_id})"
    )


def test_two_integration_triggers_same_node_unique_edge_ids():
    """
    Tests that when two IntegrationTriggers point to the same node,
    each trigger edge gets a unique ID (not duplicates).
    """

    # GIVEN two different IntegrationTriggers
    class SlackMessageTrigger(IntegrationTrigger):
        message: str

        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"

    class GithubPRTrigger(IntegrationTrigger):
        pr_title: str

        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "GITHUB"
            slug = "github_pr_opened"

    class ProcessNode(BaseNode):
        pass

    # AND a workflow where both triggers point to the same node
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = {
            SlackMessageTrigger >> ProcessNode,
            GithubPRTrigger >> ProcessNode,
        }

    # WHEN we serialize the workflow
    result = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # THEN we should have two triggers
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 2

    def get_integration_name(trigger: dict) -> str:
        exec_config = trigger.get("exec_config")
        if isinstance(exec_config, dict):
            name = exec_config.get("integration_name")
            return str(name) if name else ""
        return ""

    slack_trigger = next(
        (t for t in triggers if isinstance(t, dict) and get_integration_name(t) == "SLACK"),
        None,
    )
    assert slack_trigger is not None
    assert isinstance(slack_trigger, dict)
    slack_trigger_id = slack_trigger["id"]

    github_trigger = next(
        (t for t in triggers if isinstance(t, dict) and get_integration_name(t) == "GITHUB"),
        None,
    )
    assert github_trigger is not None
    assert isinstance(github_trigger, dict)
    github_trigger_id = github_trigger["id"]

    # AND we should have edges from both triggers
    workflow_raw_data = result["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)
    edges = workflow_raw_data["edges"]
    assert isinstance(edges, list)

    nodes = workflow_raw_data["nodes"]
    assert isinstance(nodes, list)
    process_nodes = [n for n in nodes if isinstance(n, dict) and n.get("type") not in ("TERMINAL", "ENTRYPOINT")]
    assert len(process_nodes) > 0
    process_node = process_nodes[0]
    assert isinstance(process_node, dict)
    process_node_id = process_node["id"]

    slack_edge = next(
        (
            e
            for e in edges
            if isinstance(e, dict)
            and e.get("source_node_id") == slack_trigger_id
            and e.get("target_node_id") == process_node_id
        ),
        None,
    )
    assert slack_edge is not None, "Should have edge from Slack trigger to ProcessNode"
    assert isinstance(slack_edge, dict)

    github_edge = next(
        (
            e
            for e in edges
            if isinstance(e, dict)
            and e.get("source_node_id") == github_trigger_id
            and e.get("target_node_id") == process_node_id
        ),
        None,
    )
    assert github_edge is not None, "Should have edge from GitHub trigger to ProcessNode"
    assert isinstance(github_edge, dict)

    # AND the edge IDs should be unique (not duplicates)
    assert slack_edge["id"] != github_edge["id"], (
        f"Edge IDs should be unique but both are {slack_edge['id']}. "
        "Multiple triggers targeting the same node should have distinct edge IDs."
    )
