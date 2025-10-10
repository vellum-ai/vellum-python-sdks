"""Tests for serialization of workflows with SlackTrigger."""

try:  # Python 3.9 compatibility
    from typing import TypeGuard
except ImportError:  # pragma: no cover - fallback for older runtimes
    from typing_extensions import TypeGuard  # type: ignore[assignment]

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.slack import SlackTrigger
from vellum.workflows.types.core import Json, JsonArray, JsonObject
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class Inputs(BaseInputs):
    input: str


class SimpleNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input


def is_json_array(value: Json) -> TypeGuard[JsonArray]:
    return isinstance(value, list)


def is_json_object(value: Json) -> TypeGuard[JsonObject]:
    return isinstance(value, dict)


def is_json_str(value: Json) -> TypeGuard[str]:
    return isinstance(value, str)


def test_slack_trigger_serialization() -> None:
    """Workflow with SlackTrigger serializes with triggers field."""

    class TestWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = SlackTrigger >> SimpleNode

        class Outputs(BaseWorkflow.Outputs):
            output = SimpleNode.Outputs.output

    result = get_workflow_display(workflow_class=TestWorkflow).serialize()

    triggers_value = result["triggers"]
    assert is_json_array(triggers_value)
    triggers = triggers_value

    assert len(triggers) == 1
    trigger_value = triggers[0]
    assert is_json_object(trigger_value)
    trigger = trigger_value

    trigger_type_value = trigger["type"]
    assert is_json_str(trigger_type_value)
    assert trigger_type_value == "SLACK_MESSAGE"

    assert "id" in trigger
    attributes_value = trigger["attributes"]
    assert is_json_array(attributes_value)
    assert attributes_value == []


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

    triggers_value = result["triggers"]
    assert is_json_array(triggers_value)
    triggers = triggers_value

    workflow_data_value = result["workflow_raw_data"]
    assert is_json_object(workflow_data_value)
    workflow_data = workflow_data_value

    nodes_value = workflow_data["nodes"]
    assert is_json_array(nodes_value)
    nodes = nodes_value

    assert len(triggers) == 1
    trigger_value = triggers[0]
    assert is_json_object(trigger_value)
    trigger = trigger_value

    trigger_type_value = trigger["type"]
    assert is_json_str(trigger_type_value)
    assert trigger_type_value == "SLACK_MESSAGE"

    generic_nodes = []
    for node in nodes:
        assert is_json_object(node)
        node_type_value = node.get("type")
        assert node_type_value is not None
        assert is_json_str(node_type_value)
        if node_type_value == "GENERIC":
            generic_nodes.append(node)

    assert len(generic_nodes) >= 2


def test_serialized_slack_workflow_structure() -> None:
    """Verify complete structure of serialized workflow with SlackTrigger."""

    class TestWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = SlackTrigger >> SimpleNode

        class Outputs(BaseWorkflow.Outputs):
            output = SimpleNode.Outputs.output

    result = get_workflow_display(workflow_class=TestWorkflow).serialize()

    workflow_raw_data_value = result["workflow_raw_data"]
    assert is_json_object(workflow_raw_data_value)
    workflow_raw_data = workflow_raw_data_value

    definition_value = workflow_raw_data["definition"]
    assert is_json_object(definition_value)
    definition = definition_value

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

    definition_name = definition["name"]
    assert is_json_str(definition_name)
    assert definition_name == "TestWorkflow"
