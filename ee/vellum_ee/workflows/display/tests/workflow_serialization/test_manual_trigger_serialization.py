"""Tests for serialization of workflows with ManualTrigger."""

import pytest
from typing import cast

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.base import BaseTrigger
from vellum.workflows.triggers.manual import ManualTrigger
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class Inputs(BaseInputs):
    input: str


class SimpleNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input


def create_workflow(trigger=None):
    """Factory for creating test workflows."""

    class TestWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = trigger >> SimpleNode if trigger else SimpleNode

        class Outputs(BaseWorkflow.Outputs):
            output = SimpleNode.Outputs.output

    return TestWorkflow


def serialize(workflow_class) -> JsonObject:
    """Helper to serialize a workflow."""
    return get_workflow_display(workflow_class=workflow_class).serialize()


def test_manual_trigger_serialization():
    """Workflow with ManualTrigger serializes with triggers field."""
    result = serialize(create_workflow(ManualTrigger))
    triggers = cast(JsonArray, result["triggers"])

    assert len(triggers) == 1
    trigger = cast(JsonObject, triggers[0])

    assert trigger["type"] == "MANUAL"
    assert "id" in trigger
    assert "attributes" in trigger
    assert trigger["attributes"] == []
    assert "definition" not in trigger


def test_no_trigger_serialization():
    """Workflow without trigger has no triggers field."""
    result = serialize(create_workflow())
    assert "triggers" not in result


def test_manual_trigger_multiple_entrypoints():
    """ManualTrigger with multiple entrypoints."""

    class NodeA(BaseNode):
        class Outputs(BaseNode.Outputs):
            output = Inputs.input

    class NodeB(BaseNode):
        class Outputs(BaseNode.Outputs):
            output = Inputs.input

    class MultiWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = ManualTrigger >> {NodeA, NodeB}

        class Outputs(BaseWorkflow.Outputs):
            output_a = NodeA.Outputs.output
            output_b = NodeB.Outputs.output

    result = serialize(MultiWorkflow)
    triggers = cast(JsonArray, result["triggers"])
    workflow_data = cast(JsonObject, result["workflow_raw_data"])
    nodes = cast(JsonArray, workflow_data["nodes"])

    assert len(triggers) == 1
    trigger = cast(JsonObject, triggers[0])
    assert trigger["type"] == "MANUAL"
    assert len([n for n in nodes if cast(JsonObject, n)["type"] == "GENERIC"]) >= 2


def test_serialized_workflow_structure():
    """Verify complete structure of serialized workflow."""
    result = serialize(create_workflow(ManualTrigger))
    workflow_raw_data = cast(JsonObject, result["workflow_raw_data"])
    definition = cast(JsonObject, workflow_raw_data["definition"])

    assert result.keys() == {"workflow_raw_data", "input_variables", "state_variables", "output_variables", "triggers"}
    assert workflow_raw_data.keys() == {"nodes", "edges", "display_data", "definition", "output_values"}
    assert definition["name"] == "TestWorkflow"


def test_unknown_trigger_type():
    """Unknown trigger types raise ValueError."""

    class UnknownTrigger(BaseTrigger):
        pass

    with pytest.raises(ValueError, match="Unknown trigger type: UnknownTrigger"):
        serialize(create_workflow(UnknownTrigger))
