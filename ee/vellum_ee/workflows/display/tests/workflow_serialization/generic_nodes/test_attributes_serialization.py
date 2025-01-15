from uuid import uuid4

from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum_ee.workflows.display.base import WorkflowInputsDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.nodes.vellum.base_node import BaseNodeDisplay


class Inputs(BaseInputs):
    input: str


class ConstantValueGenericNode(BaseNode):
    attr: str = "hello"


def test_serialize_node__constant_value(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=ConstantValueGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    assert not DeepDiff(
        {
            "id": "be892bc8-e4de-47ef-ab89-dc9d869af1fe",
            "label": "ConstantValueGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "ConstantValueGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_attributes_serialization",
                ],
            },
            "trigger": {"id": "279e8228-9b82-43a3-8c31-affc036e3a0b", "merge_behavior": "AWAIT_ANY"},
            "ports": [{"id": "e6cf13b0-5590-421c-84f2-5a0b169677e1", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "4cbbfd98-9ab6-41a8-bf4e-ae65f0eafe47",
                    "name": "attr",
                    "value": {
                        "type": "CONSTANT_VALUE",
                        "value": {
                            "type": "STRING",
                            "value": "hello",
                        },
                    },
                }
            ],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


class WorkflowInputGenericNode(BaseNode):
    attr: str = Inputs.input


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
                    "test_attributes_serialization",
                ],
            },
            "trigger": {"id": "b1a5d749-bac0-4f11-8427-191febb2198e", "merge_behavior": "AWAIT_ANY"},
            "ports": [{"id": "f013bf3f-49f6-41cd-ac13-7439b71a304a", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "56d44313-cfdd-4d75-9b19-0beb94e59c4e",
                    "name": "attr",
                    "value": {
                        "type": "WORKFLOW_INPUT",
                        "input_variable_id": str(input_id),
                    },
                }
            ],
            "outputs": [],
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
    attr = NodeWithOutput.Outputs.output


def test_serialize_node__node_output(serialize_node):
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
                    "test_attributes_serialization",
                ],
            },
            "trigger": {"id": "449072ba-f7b6-4314-ac96-682123f225e5", "merge_behavior": "AWAIT_ANY"},
            "ports": [{"id": "ec9a79b8-65c3-4de8-bd29-42c914d72d4f", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "73e6a103-1339-41ec-a245-42d43b0637c1",
                    "name": "attr",
                    "value": {
                        "type": "NODE_OUTPUT",
                        "node_id": "cd954d76-0b0a-4d9b-9bdf-347179c38cb6",
                        "node_output_id": str(node_output_id),
                    },
                }
            ],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


class VellumSecretGenericNode(BaseNode):
    attr = VellumSecretReference(name="hello")


def test_serialize_node__vellum_secret(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=VellumSecretGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )
    assert not DeepDiff(
        {
            "id": "89aa6faa-b533-4179-8912-70a048bf0712",
            "label": "VellumSecretGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "VellumSecretGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_attributes_serialization",
                ],
            },
            "trigger": {"id": "3ea0305d-d8ea-45fe-8cf1-f6c1c85e6979", "merge_behavior": "AWAIT_ANY"},
            "ports": [{"id": "69e49322-8f8a-42d2-b36f-3fbe53dad616", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "8edd27da-eec1-4539-8bec-629b5ef7a9f9",
                    "name": "attr",
                    "value": {"type": "VELLUM_SECRET", "vellum_secret_name": "hello"},
                }
            ],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


class NodeWithExecutions(BaseNode):
    pass


class NodeWithExecutionsDisplay(BaseNodeDisplay[NodeWithExecutions]):
    pass


class GenericNodeReferencingExecutions(BaseNode):
    attr: int = NodeWithExecutions.Execution.count


def test_serialize_node__node_execution(serialize_node):
    workflow_input_id = uuid4()
    serialized_node = serialize_node(
        node_class=GenericNodeReferencingExecutions,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=workflow_input_id)},
        global_node_displays={NodeWithExecutions: NodeWithExecutionsDisplay()},
    )

    assert not DeepDiff(
        {
            "id": "6e4d2fb7-891e-492e-97a1-adf44693f518",
            "label": "GenericNodeReferencingExecutions",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "GenericNodeReferencingExecutions",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_attributes_serialization",
                ],
            },
            "trigger": {"id": "68a91426-4c30-4194-a4c0-cff224d3c0f3", "merge_behavior": "AWAIT_ANY"},
            "ports": [{"id": "1794c2eb-5cab-49fe-9354-dfc29f11b374", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "090e18d7-d5b9-4d5f-9aec-0f562e4b33a8",
                    "name": "attr",
                    "value": {
                        "type": "EXECUTION_COUNTER",
                        "node_id": "c09bd5a6-dc04-4036-90d4-580acd43c71f",
                    },
                }
            ],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )
