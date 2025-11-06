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
            "id": "e33ddf79-f48c-4057-ba17-d41a3a60ac98",
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
            "trigger": {"id": "e66c7dde-02c9-4f6d-84a6-16117b54cd88", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "d83b7a5d-bbac-47ee-9277-1fbed71e83e8", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [],
            "outputs": [
                {
                    "id": "0fd1356f-ca4e-4e85-b923-8a0164bfc451",
                    "name": "output",
                    "type": "NUMBER",
                    "value": None,
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
            "id": "8ad5d3b2-4d4d-494f-ab5c-caa650a397e9",
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
            "trigger": {"id": "f8a79f35-b083-47d1-80ee-5efc2baa54e5", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "78878dd7-87fc-4f93-b340-0e1155260f23", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [],
            "outputs": [
                {
                    "id": "b62c0cbe-48d5-465d-8d9e-4ff82847f8c7",
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
            "id": "e5387a2f-ccff-43b2-8b29-8f4ba9beb01e",
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
            "trigger": {"id": "c43b6517-102a-44bc-83c8-37d42861d3e6", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "383dc10a-d8f3-4bac-b995-8b95bc6deb21", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [],
            "outputs": [
                {
                    "id": "46e6e98e-9ecf-4880-86f9-6390f0851c31",
                    "name": "output",
                    "type": "STRING",
                    "value": {
                        "type": "NODE_OUTPUT",
                        "node_id": "242ad818-12ec-449f-87b4-d2bc513e2148",
                        "node_output_id": str(node_output_id),
                    },
                }
            ],
        },
        serialized_node,
        ignore_order=True,
    )
