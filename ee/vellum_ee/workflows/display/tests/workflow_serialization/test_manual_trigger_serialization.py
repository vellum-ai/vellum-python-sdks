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
    assert triggers[0] == {"id": "b3c8ab56-001f-4157-bbc2-4a7fe5ebf8c6", "type": "MANUAL", "attributes": []}


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

    # entrypoint + 2 nodes
    assert len(nodes) == 3

    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)

    assert len(triggers) == 1
    assert triggers[0] == {"id": "b3c8ab56-001f-4157-bbc2-4a7fe5ebf8c6", "type": "MANUAL", "attributes": []}


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


def test_manual_trigger_entrypoint_id_consistency():
    """ManualTrigger ID matches entrypoint node ID for backward compatibility."""

    class SimpleNode(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = ManualTrigger >> SimpleNode

    result = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # Get trigger ID
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1
    trigger = triggers[0]
    assert isinstance(trigger, dict)
    trigger_id = trigger["id"]

    # Get entrypoint node ID - ManualTrigger workflows still use ENTRYPOINT nodes
    workflow_raw_data = result["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)
    nodes = workflow_raw_data["nodes"]
    assert isinstance(nodes, list)
    entrypoint_nodes = [n for n in nodes if isinstance(n, dict) and n["type"] == "ENTRYPOINT"]
    assert len(entrypoint_nodes) == 1, "ManualTrigger workflows should have ENTRYPOINT node for backward compatibility"
    entrypoint_id = entrypoint_nodes[0]["id"]

    # Verify IDs match
    assert trigger_id == entrypoint_id, (
        f"ManualTrigger ID ({trigger_id}) must match entrypoint node ID ({entrypoint_id}) "
        "to maintain trigger-entrypoint linkage"
    )
    # Also verify the expected UUID
    assert trigger_id == "b3c8ab56-001f-4157-bbc2-4a7fe5ebf8c6"
