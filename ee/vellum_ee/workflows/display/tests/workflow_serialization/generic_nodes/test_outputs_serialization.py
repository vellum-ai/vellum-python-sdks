from uuid import uuid4

from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum_ee.workflows.display.base import WorkflowInputsDisplay
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay


class Inputs(BaseInputs):
    input: str


class AnnotatedOutputGenericNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output: int


def test_serialize_node__annotated_output(serialize_node):
    serialized_node = serialize_node(AnnotatedOutputGenericNode)

    assert not DeepDiff(
        {
            "id": "c0b71cfa-0d9e-4329-bde0-967c44be5c3c",
            "label": "AnnotatedOutputGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "AnnotatedOutputGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_outputs_serialization",
                ],
            },
            "trigger": {"id": "256ef76c-39a6-4a8f-8bda-922f5972a1d4", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "9f391128-5d83-4c46-a62e-2b8bd075f569", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [],
            "outputs": [
                {
                    "id": "8c3c9aff-e1d5-49f4-af75-3ec2fcbb4af2",
                    "name": "output",
                    "type": "NUMBER",
                    "value": None,
                }
            ],
        },
        serialized_node,
        ignore_order=True,
    )


class WorkflowInputGenericNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input


def test_serialize_node__workflow_input(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=WorkflowInputGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    assert not DeepDiff(
        {
            "id": "ddfa947f-0830-476b-b07e-ac573968f9a7",
            "label": "WorkflowInputGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "WorkflowInputGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_outputs_serialization",
                ],
            },
            "trigger": {"id": "b1a5d749-bac0-4f11-8427-191febb2198e", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "d15c7175-139c-4885-8ef8-3e4081db121b", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [],
            "outputs": [
                {
                    "id": "2c4a85c0-b017-4cea-a261-e8e8498570c9",
                    "name": "output",
                    "type": "STRING",
                    "value": {
                        "type": "WORKFLOW_INPUT",
                        "input_variable_id": str(input_id),
                    },
                }
            ],
        },
        serialized_node,
        ignore_order=True,
    )


class NodeWithOutput(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input


class NodeWithOutputDisplay(BaseNodeDisplay[NodeWithOutput]):
    pass


class GenericNodeReferencingOutput(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = NodeWithOutput.Outputs.output


def test_serialize_node__node_output_reference(serialize_node):
    workflow_input_id = uuid4()
    node_output_id = uuid4()
    serialized_node = serialize_node(
        node_class=GenericNodeReferencingOutput,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=workflow_input_id)},
        global_node_displays={NodeWithOutput: NodeWithOutputDisplay()},
        global_node_output_displays={
            NodeWithOutput.Outputs.output: (NodeWithOutput, NodeOutputDisplay(id=node_output_id, name="output"))
        },
    )

    assert not DeepDiff(
        {
            "id": "c1e2ce60-ac3a-4b17-915e-abe861734e03",
            "label": "GenericNodeReferencingOutput",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "GenericNodeReferencingOutput",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_outputs_serialization",
                ],
            },
            "trigger": {"id": "449072ba-f7b6-4314-ac96-682123f225e5", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "1879f33e-6efa-46a0-9281-e02bbbc1d413", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [],
            "outputs": [
                {
                    "id": "db010db3-7076-4df9-ae1b-069caa16fa20",
                    "name": "output",
                    "type": "STRING",
                    "value": {
                        "type": "NODE_OUTPUT",
                        "node_id": "cd954d76-0b0a-4d9b-9bdf-347179c38cb6",
                        "node_output_id": str(node_output_id),
                    },
                }
            ],
        },
        serialized_node,
        ignore_order=True,
    )
