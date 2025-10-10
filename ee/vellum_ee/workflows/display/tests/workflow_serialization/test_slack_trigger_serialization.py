"""Tests for serialization of workflows with SlackTrigger."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.slack import SlackTrigger
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

    # Validate triggers structure
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1

    trigger = triggers[0]
    assert isinstance(trigger, dict)
    assert trigger["type"] == "SLACK_MESSAGE"
    assert "id" in trigger

    # Validate attributes
    assert "attributes" in trigger
    attributes = trigger["attributes"]
    assert isinstance(attributes, list)
    assert len(attributes) == 6

    attribute_names = set()
    for attribute in attributes:
        assert isinstance(attribute, dict)
        assert "name" in attribute
        assert isinstance(attribute["name"], str)
        attribute_names.add(attribute["name"])
    assert attribute_names == {
        "message",
        "channel",
        "user",
        "timestamp",
        "thread_ts",
        "event_type",
    }

    for attribute in attributes:
        assert isinstance(attribute, dict)
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

    # Validate triggers
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1

    trigger = triggers[0]
    assert isinstance(trigger, dict)
    assert trigger["type"] == "SLACK_MESSAGE"

    # Validate attributes
    assert "attributes" in trigger
    attributes = trigger["attributes"]
    assert isinstance(attributes, list)
    attribute_names = set()
    for attribute in attributes:
        assert isinstance(attribute, dict)
        assert "name" in attribute
        assert isinstance(attribute["name"], str)
        attribute_names.add(attribute["name"])

    assert attribute_names == {
        "message",
        "channel",
        "user",
        "timestamp",
        "thread_ts",
        "event_type",
    }

    # Validate nodes
    assert "workflow_raw_data" in result
    workflow_data = result["workflow_raw_data"]
    assert isinstance(workflow_data, dict)
    assert "nodes" in workflow_data
    nodes = workflow_data["nodes"]
    assert isinstance(nodes, list)

    generic_nodes = [node for node in nodes if isinstance(node, dict) and node.get("type") == "GENERIC"]
    assert len(generic_nodes) >= 2


def test_serialized_slack_workflow_structure() -> None:
    """Verify complete structure of serialized workflow with SlackTrigger."""

    class TestWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = SlackTrigger >> SimpleNode

        class Outputs(BaseWorkflow.Outputs):
            output = SimpleNode.Outputs.output

    result = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # Validate top-level structure
    assert isinstance(result, dict)
    assert set(result.keys()) == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
        "triggers",
    }

    # Validate workflow_raw_data structure
    workflow_raw_data = result["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)
    assert set(workflow_raw_data.keys()) == {
        "nodes",
        "edges",
        "display_data",
        "definition",
        "output_values",
    }

    # Validate definition
    definition = workflow_raw_data["definition"]
    assert isinstance(definition, dict)
    assert definition["name"] == "TestWorkflow"
