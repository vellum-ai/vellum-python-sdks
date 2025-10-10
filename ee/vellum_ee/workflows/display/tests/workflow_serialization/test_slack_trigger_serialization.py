"""Tests for serialization of workflows with SlackTrigger."""

from typing import cast

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


def test_slack_trigger_serialization() -> None:
    """Workflow with SlackTrigger serializes with triggers field."""

    class TestWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = SlackTrigger >> SimpleNode

        class Outputs(BaseWorkflow.Outputs):
            output = SimpleNode.Outputs.output

    result = get_workflow_display(workflow_class=TestWorkflow).serialize()

    triggers = cast(JsonArray, result["triggers"])
    assert len(triggers) == 1

    trigger = cast(JsonObject, triggers[0])
    assert trigger["type"] == "SLACK_MESSAGE"
    assert "id" in trigger

    attributes = cast(JsonArray, trigger["attributes"])
    assert len(attributes) == 6

    attribute_names = {cast(JsonObject, attr)["name"] for attr in attributes}
    assert attribute_names == {
        "message",
        "channel",
        "user",
        "timestamp",
        "thread_ts",
        "event_type",
    }

    for attr in attributes:
        attribute = cast(JsonObject, attr)
        assert attribute["value"] is None
        assert isinstance(attribute["id"], str)
        assert attribute["id"]


def test_slack_trigger_multiple_entrypoints() -> None:
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

    triggers = cast(JsonArray, result["triggers"])
    workflow_data = cast(JsonObject, result["workflow_raw_data"])
    nodes = cast(JsonArray, workflow_data["nodes"])

    assert len(triggers) == 1
    trigger = cast(JsonObject, triggers[0])
    assert trigger["type"] == "SLACK_MESSAGE"

    attributes = cast(JsonArray, trigger["attributes"])
    assert {cast(JsonObject, attr)["name"] for attr in attributes} == {
        "message",
        "channel",
        "user",
        "timestamp",
        "thread_ts",
        "event_type",
    }

    generic_nodes = []
    for node in nodes:
        node_obj = cast(JsonObject, node)
        if node_obj.get("type") == "GENERIC":
            generic_nodes.append(node_obj)
    assert len(generic_nodes) >= 2


def test_serialized_slack_workflow_structure() -> None:
    """Verify complete structure of serialized workflow with SlackTrigger."""

    class TestWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = SlackTrigger >> SimpleNode

        class Outputs(BaseWorkflow.Outputs):
            output = SimpleNode.Outputs.output

    result = get_workflow_display(workflow_class=TestWorkflow).serialize()

    workflow_raw_data = cast(JsonObject, result["workflow_raw_data"])
    definition = cast(JsonObject, workflow_raw_data["definition"])

    assert set(result.keys()) == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
        "triggers",
    }

    assert set(workflow_raw_data.keys()) == {
        "nodes",
        "edges",
        "display_data",
        "definition",
        "output_values",
    }

    assert definition["name"] == "TestWorkflow"
