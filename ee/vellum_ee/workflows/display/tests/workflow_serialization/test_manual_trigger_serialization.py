import pytest

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.base import BaseTrigger
from vellum.workflows.triggers.manual import ManualTrigger
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_manual_trigger_serialization():
    """Workflow with ManualTrigger serializes with triggers field."""

    class SimpleNode(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = ManualTrigger >> SimpleNode

    result = get_workflow_display(workflow_class=TestWorkflow).serialize()
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)

    assert len(triggers) == 1
    assert triggers[0] == {"id": "b09c1902-3cca-4c79-b775-4c32e3e88466", "type": "MANUAL", "attributes": []}


def test_manual_trigger_multiple_entrypoints():
    """ManualTrigger with multiple entrypoints."""

    class NodeA(BaseNode):
        pass

    class NodeB(BaseNode):
        pass

    class MultiWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = ManualTrigger >> {NodeA, NodeB}

    result = get_workflow_display(workflow_class=MultiWorkflow).serialize()
    workflow_data = result["workflow_raw_data"]
    assert isinstance(workflow_data, dict)
    assert "nodes" in workflow_data
    nodes = workflow_data["nodes"]
    assert isinstance(nodes, list)

    # With triggers, 3 nodes exist: ENTRYPOINT (for backwards compat) + 2 actual nodes
    assert len(nodes) == 3

    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)

    assert len(triggers) == 1
    assert triggers[0] == {"id": "b09c1902-3cca-4c79-b775-4c32e3e88466", "type": "MANUAL", "attributes": []}


def test_manual_trigger_entrypoint_node_id():
    """
    Backwards compatibility: Workflows with triggers should have an ENTRYPOINT node
    whose ID matches the trigger ID.

    This allows existing systems that expect ENTRYPOINT nodes to continue working,
    while linking the entrypoint to the trigger through shared ID.
    """

    class FirstNode(BaseNode):
        pass

    class SecondNode(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = ManualTrigger >> FirstNode >> SecondNode

    result = get_workflow_display(workflow_class=TestWorkflow).serialize()
    assert isinstance(result, dict)

    # Verify trigger exists
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1

    trigger = triggers[0]
    assert isinstance(trigger, dict)
    trigger_id = trigger["id"]
    assert trigger["type"] == "MANUAL"

    # Verify ENTRYPOINT node exists for backwards compatibility
    workflow_data = result["workflow_raw_data"]
    assert isinstance(workflow_data, dict)

    nodes = workflow_data["nodes"]
    assert isinstance(nodes, list)

    # Find the ENTRYPOINT node
    entrypoint_nodes = [node for node in nodes if isinstance(node, dict) and node.get("type") == "ENTRYPOINT"]
    assert len(entrypoint_nodes) == 1, (
        "Workflows with triggers should have exactly one ENTRYPOINT node for backwards compatibility. "
        f"Found {len(entrypoint_nodes)} ENTRYPOINT node(s)."
    )

    # KEY ASSERTION: Entrypoint node ID should match trigger ID
    entrypoint_node = entrypoint_nodes[0]
    assert entrypoint_node["id"] == trigger_id, (
        f"Entrypoint node ID ({entrypoint_node['id']}) should match trigger ID ({trigger_id}) "
        "to link the entrypoint with its trigger."
    )

    # Should have 3 nodes total: ENTRYPOINT, FirstNode, SecondNode
    assert len(nodes) == 3
    node_types = {node.get("type") for node in nodes if isinstance(node, dict)}
    assert "ENTRYPOINT" in node_types
    assert "GENERIC" in node_types  # FirstNode and SecondNode are GENERIC


def test_unknown_trigger_type():
    """Unknown trigger types raise ValueError."""

    class UnknownTrigger(BaseTrigger):
        pass

    class SimpleNode(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = UnknownTrigger >> SimpleNode

    with pytest.raises(ValueError, match="Unknown trigger type: UnknownTrigger"):
        get_workflow_display(workflow_class=TestWorkflow).serialize()
