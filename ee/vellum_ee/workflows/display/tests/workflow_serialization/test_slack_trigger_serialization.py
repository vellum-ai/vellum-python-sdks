"""Tests for serialization of workflows with SlackTrigger."""

from typing import assert_type

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.slack import SlackTrigger
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class Inputs(BaseInputs):
    input: str


class SimpleNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input


def test_slack_trigger_serialization():
    """Workflow with SlackTrigger serializes with triggers field."""

    class TestWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = SlackTrigger >> SimpleNode

        class Outputs(BaseWorkflow.Outputs):
            output = SimpleNode.Outputs.output

    result = get_workflow_display(workflow_class=TestWorkflow).serialize()
    triggers = result["triggers"]
    assert_type(triggers, JsonArray)

    assert len(triggers) == 1
    trigger = triggers[0]
    assert_type(trigger, JsonObject)

    assert trigger["type"] == "SLACK_MESSAGE"
    assert "id" in trigger
    assert "attributes" in trigger
    assert trigger["attributes"] == []


def test_slack_trigger_multiple_entrypoints():
    """SlackTrigger with multiple entrypoints."""

    class NodeA(BaseNode):
        class Outputs(BaseNode.Outputs):
            output = Inputs.input

    class NodeB(BaseNode):
        class Outputs(BaseNode.Outputs):
            output = Inputs.input

    class MultiWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = SlackTrigger >> {NodeA, NodeB}

        class Outputs(BaseWorkflow.Outputs):
            output_a = NodeA.Outputs.output
            output_b = NodeB.Outputs.output

    result = get_workflow_display(workflow_class=MultiWorkflow).serialize()
    triggers = result["triggers"]
    assert_type(triggers, JsonArray)

    workflow_data = result["workflow_raw_data"]
    assert_type(workflow_data, JsonObject)

    nodes = workflow_data["nodes"]
    assert_type(nodes, JsonArray)

    assert len(triggers) == 1
    trigger = triggers[0]
    assert_type(trigger, JsonObject)
    assert trigger["type"] == "SLACK_MESSAGE"

    generic_nodes = [n for n in nodes if assert_type(n, JsonObject)["type"] == "GENERIC"]
    assert len(generic_nodes) >= 2


def test_serialized_slack_workflow_structure():
    """Verify complete structure of serialized workflow with SlackTrigger."""

    class TestWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = SlackTrigger >> SimpleNode

        class Outputs(BaseWorkflow.Outputs):
            output = SimpleNode.Outputs.output

    result = get_workflow_display(workflow_class=TestWorkflow).serialize()
    workflow_raw_data = result["workflow_raw_data"]
    assert_type(workflow_raw_data, JsonObject)

    definition = workflow_raw_data["definition"]
    assert_type(definition, JsonObject)

    assert result.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
        "triggers",
    }
    assert workflow_raw_data.keys() == {"nodes", "edges", "display_data", "definition", "output_values"}
    assert definition["name"] == "TestWorkflow"
