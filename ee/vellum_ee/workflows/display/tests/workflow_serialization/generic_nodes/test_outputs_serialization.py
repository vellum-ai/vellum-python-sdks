from uuid import uuid4

from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum_ee.workflows.display.base import WorkflowInputsDisplay
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay


class Inputs(BaseInputs):
    input: str


def test_serialize_node__annotated_output(serialize_node):
    class AnnotatedOutputGenericNode(BaseNode):

        class Outputs(BaseNode.Outputs):
            output: int

    serialized_node = serialize_node(AnnotatedOutputGenericNode)

    assert not DeepDiff(
        {
            "id": "6337349e-5718-4732-b717-b6be650c6664",
            "label": "Annotated Output Generic Node",
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
            "trigger": {"id": "e23d58ad-012b-48a2-80bc-81fe740b5785", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "2d86f771-e1b6-4e58-8af1-9b12604e9bb6", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [],
            "outputs": [
                {
                    "id": "6d08f5f4-cb29-4240-899a-d811e547a30b",
                    "name": "output",
                    "type": "NUMBER",
                    "value": None,
                    "schema": {"type": "integer"},
                }
            ],
        },
        serialized_node,
        ignore_order=True,
    )


def test_serialize_node__workflow_input(serialize_node):
    class WorkflowInputGenericNode(BaseNode):

        class Outputs(BaseNode.Outputs):
            output = Inputs.input

    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=WorkflowInputGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    assert not DeepDiff(
        {
            "id": "b8b45ce8-b897-4347-a8ad-45e0576fcf59",
            "label": "Workflow Input Generic Node",
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
            "trigger": {"id": "6fb30c9c-b9f0-452f-99f5-58d484b89882", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "8997d239-eefb-4006-8961-a8241829b433", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [],
            "outputs": [
                {
                    "id": "70c7e4c8-2ad3-4093-b69f-a83b4e2a8167",
                    "name": "output",
                    "type": "STRING",
                    "value": {
                        "type": "WORKFLOW_INPUT",
                        "input_variable_id": str(input_id),
                    },
                    "schema": {"type": "string"},
                }
            ],
        },
        serialized_node,
        ignore_order=True,
    )


def test_serialize_node__node_output_reference(serialize_node):
    class NodeWithOutput(BaseNode):

        class Outputs(BaseNode.Outputs):
            output = Inputs.input

    class NodeWithOutputDisplay(BaseNodeDisplay[NodeWithOutput]):
        pass

    class GenericNodeReferencingOutput(BaseNode):

        class Outputs(BaseNode.Outputs):
            output = NodeWithOutput.Outputs.output

    workflow_input_id = uuid4()
    node_output_id = uuid4()
    serialized_node = serialize_node(
        node_class=GenericNodeReferencingOutput,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=workflow_input_id)},
        global_node_displays={NodeWithOutput: NodeWithOutputDisplay()},
        global_node_output_displays={
            NodeWithOutput.Outputs.output: NodeOutputDisplay(id=node_output_id, name="output")
        },
    )

    assert not DeepDiff(
        {
            "id": "a3a63eb0-ed79-41c1-9bd2-c4b3d69c3017",
            "label": "Generic Node Referencing Output",
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
            "trigger": {"id": "b12c8ed6-42e2-4dad-9a39-adb1650a6f85", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "3953fe95-7ea9-49ce-a45f-cc55c0f0b9a4", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [],
            "outputs": [
                {
                    "id": "72f37d68-c927-4f4e-8b25-72e8cb2c7f5c",
                    "name": "output",
                    "type": "STRING",
                    "value": {
                        "type": "NODE_OUTPUT",
                        "node_id": "40fcba1f-9b25-4fed-8f15-a2fd80ff85a1",
                        "node_output_id": str(node_output_id),
                    },
                    "schema": {"type": "string"},
                }
            ],
        },
        serialized_node,
        ignore_order=True,
    )
