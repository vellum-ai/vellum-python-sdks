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


def test_slack_trigger_serialization():
    """Workflow with SlackTrigger serializes with triggers field and outputs."""
    result = serialize(create_workflow(SlackTrigger))
    triggers = cast(JsonArray, result["triggers"])

    assert len(triggers) == 1
    trigger = cast(JsonObject, triggers[0])

    assert trigger["type"] == "SLACK_MESSAGE"
    assert "id" in trigger
    assert "attributes" in trigger
    assert trigger["attributes"] == []

    # Check that outputs are included
    assert "outputs" in trigger
    outputs = cast(JsonArray, trigger["outputs"])
    assert len(outputs) == 6  # message, channel, user, timestamp, thread_ts, event_type

    # Verify output structure
    output_names = {cast(JsonObject, output)["name"] for output in outputs}
    assert output_names == {"message", "channel", "user", "timestamp", "thread_ts", "event_type"}

    # Verify output types (all should be STRING for SlackTrigger)
    for output in outputs:
        output_obj = cast(JsonObject, output)
        assert output_obj["type"] == "STRING"


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

    result = serialize(MultiWorkflow)
    triggers = cast(JsonArray, result["triggers"])
    workflow_data = cast(JsonObject, result["workflow_raw_data"])
    nodes = cast(JsonArray, workflow_data["nodes"])

    assert len(triggers) == 1
    trigger = cast(JsonObject, triggers[0])
    assert trigger["type"] == "SLACK_MESSAGE"
    assert "outputs" in trigger
    assert len([n for n in nodes if cast(JsonObject, n)["type"] == "GENERIC"]) >= 2


def test_serialized_slack_workflow_structure():
    """Verify complete structure of serialized workflow with SlackTrigger."""
    result = serialize(create_workflow(SlackTrigger))
    workflow_raw_data = cast(JsonObject, result["workflow_raw_data"])
    definition = cast(JsonObject, workflow_raw_data["definition"])

    assert result.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
        "triggers",
    }
    assert workflow_raw_data.keys() == {"nodes", "edges", "display_data", "definition", "output_values"}
    assert definition["name"] == "TestWorkflow"


def test_slack_trigger_outputs_correct_fields():
    """Verify SlackTrigger outputs contain all expected fields."""
    result = serialize(create_workflow(SlackTrigger))
    triggers = cast(JsonArray, result["triggers"])
    trigger = cast(JsonObject, triggers[0])
    outputs = cast(JsonArray, trigger["outputs"])

    # Convert to dict for easy lookup
    outputs_dict = {cast(JsonObject, o)["name"]: cast(JsonObject, o) for o in outputs}

    # Verify all required fields
    assert "message" in outputs_dict
    assert "channel" in outputs_dict
    assert "user" in outputs_dict
    assert "timestamp" in outputs_dict
    assert "thread_ts" in outputs_dict
    assert "event_type" in outputs_dict

    # All should be STRING type
    for field_name in ["message", "channel", "user", "timestamp", "thread_ts", "event_type"]:
        assert outputs_dict[field_name]["type"] == "STRING"
