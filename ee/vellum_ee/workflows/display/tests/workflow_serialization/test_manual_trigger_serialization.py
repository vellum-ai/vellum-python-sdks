"""Tests for serialization of workflows with ManualTrigger."""

from deepdiff import DeepDiff

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.manual import ManualTrigger
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class Inputs(BaseInputs):
    input: str


class SimpleNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input


class ManualTriggerWorkflow(BaseWorkflow[Inputs, BaseState]):
    """Workflow with explicit ManualTrigger."""

    graph = ManualTrigger >> SimpleNode

    class Outputs(BaseWorkflow.Outputs):
        output = SimpleNode.Outputs.output


class ImplicitTriggerWorkflow(BaseWorkflow[Inputs, BaseState]):
    """Workflow without explicit trigger (should have no trigger in serialization)."""

    graph = SimpleNode

    class Outputs(BaseWorkflow.Outputs):
        output = SimpleNode.Outputs.output


def test_serialize_workflow_with_manual_trigger():
    """Test that a workflow with ManualTrigger serializes correctly."""
    # GIVEN a Workflow with explicit ManualTrigger
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=ManualTriggerWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the workflow_raw_data should contain trigger information
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert "trigger" in workflow_raw_data

    # AND the trigger should be of type MANUAL
    trigger = workflow_raw_data["trigger"]
    assert not DeepDiff(
        {
            "type": "MANUAL",
            "definition": {
                "name": "ManualTrigger",
                "module": ["vellum", "workflows", "triggers", "manual"],
            },
        },
        trigger,
        ignore_order=True,
    )


def test_serialize_workflow_without_trigger():
    """Test that a workflow without explicit trigger has no trigger field."""
    # GIVEN a Workflow without explicit trigger
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=ImplicitTriggerWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the workflow_raw_data should NOT contain trigger information
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert "trigger" not in workflow_raw_data


def test_serialize_workflow_with_manual_trigger_multiple_entrypoints():
    """Test serialization with ManualTrigger >> {NodeA, NodeB}."""

    class NodeA(BaseNode):
        class Outputs(BaseNode.Outputs):
            output = Inputs.input

    class NodeB(BaseNode):
        class Outputs(BaseNode.Outputs):
            output = Inputs.input

    class MultiEntrypointWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = ManualTrigger >> {NodeA, NodeB}

        class Outputs(BaseWorkflow.Outputs):
            output_a = NodeA.Outputs.output
            output_b = NodeB.Outputs.output

    # GIVEN a Workflow with ManualTrigger >> {NodeA, NodeB}
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=MultiEntrypointWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the workflow should have trigger information
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert "trigger" in workflow_raw_data

    # AND the trigger should be MANUAL
    trigger = workflow_raw_data["trigger"]
    assert trigger["type"] == "MANUAL"
    assert trigger["definition"]["name"] == "ManualTrigger"

    # AND the workflow should have both nodes as entrypoints
    nodes = workflow_raw_data["nodes"]
    node_types = [node["type"] for node in nodes]

    # Should have: ENTRYPOINT, NodeA, NodeB, and 2 TERMINAL nodes (for outputs)
    assert "ENTRYPOINT" in node_types
    assert len([n for n in nodes if n["type"] == "GENERIC"]) >= 2


def test_serialize_workflow_full_structure():
    """Test complete structure of serialized workflow with trigger."""
    # GIVEN a Workflow with ManualTrigger
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=ManualTriggerWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN it should have the standard keys
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND the workflow_raw_data should have all expected keys
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    expected_keys = {"nodes", "edges", "display_data", "definition", "output_values", "trigger"}
    assert workflow_raw_data.keys() == expected_keys

    # AND the definition should identify the workflow correctly
    definition = workflow_raw_data["definition"]
    assert definition["name"] == "ManualTriggerWorkflow"
    assert "workflow_serialization" in ".".join(definition["module"])
