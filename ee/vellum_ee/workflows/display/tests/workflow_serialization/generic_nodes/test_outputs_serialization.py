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
            "label": "test_serialize_node__annotated_output.<locals>.AnnotatedOutputGenericNode",
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
            "id": "30116483-6f38-40e0-baf2-32de0e14e9a3",
            "label": "test_serialize_node__workflow_input.<locals>.WorkflowInputGenericNode",
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
            "trigger": {"id": "debf37b9-720d-48dd-9699-69283966f927", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "20d91130-ca86-4420-b2e7-a962c0f1a509", "type": "DEFAULT", "name": "default"}],
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
            NodeWithOutput.Outputs.output: (NodeWithOutput, NodeOutputDisplay(id=node_output_id, name="output"))
        },
    )

    assert not DeepDiff(
        {
            "id": "ac067acc-6a6f-44b1-ae84-428e965ce691",
            "label": "test_serialize_node__node_output_reference.<locals>.GenericNodeReferencingOutput",
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
            "trigger": {"id": "c8804b97-9f84-41b6-ade8-aa74544d6846", "merge_behavior": "AWAIT_ATTRIBUTES"},
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
                        "node_id": "21213d1e-991c-405a-b4fa-a1e01c4dd088",
                        "node_output_id": str(node_output_id),
                    },
                }
            ],
        },
        serialized_node,
        ignore_order=True,
    )
