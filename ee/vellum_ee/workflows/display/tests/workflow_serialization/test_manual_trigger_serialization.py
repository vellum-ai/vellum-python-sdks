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

    # entrypoint + 2 nodes
    assert len(nodes) == 3

    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)

    assert len(triggers) == 1
    assert triggers[0] == {"id": "b09c1902-3cca-4c79-b775-4c32e3e88466", "type": "MANUAL", "attributes": []}


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
