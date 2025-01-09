from uuid import uuid4

from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.ports.port import Port

from ee.vellum_ee.workflows.display.base import WorkflowInputsDisplay


class Inputs(BaseInputs):
    input: str


class BasicGenericNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input


def test_serialize_node__basic(serialize_node):
    serialized_node = serialize_node(BasicGenericNode)
    assert not DeepDiff(
        {
            "id": "c2ed23f7-f6cb-4a56-a91c-2e5f9d8fda7f",
            "label": "BasicGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "definition": {
                "name": "BasicGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_ports_serialization",
                ],
                "bases": [{"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]}],
            },
            "trigger": {"id": "9d3a1b3d-4a38-4f2e-bbf1-dd8be152bce8", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "4fbf0fff-a42e-4410-852a-238b5059198e",
                    "type": "DEFAULT",
                }
            ],
            "adornments": None,
            "attributes": [],
        },
        serialized_node,
        ignore_order=True,
    )


class IfGenericNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input

    class Ports(BaseNode.Ports):
        if_branch = Port.on_if(Inputs.input.equals("hello"))


def test_serialize_node__if(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=IfGenericNode, global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)}
    )

    assert not DeepDiff(
        {
            "id": "31da54ae-1abb-4e9e-8a7d-6f4f30a78c72",
            "label": "IfGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "definition": {
                "name": "IfGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_ports_serialization",
                ],
                "bases": [{"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]}],
            },
            "trigger": {"id": "a8afaebc-7333-4e3f-b221-24452b4a1d47", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "7605b4c0-a432-4517-b759-5858045a5146",
                    "type": "IF",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
                            "type": "WORKFLOW_INPUT",
                            "input_variable_id": str(input_id),
                        },
                        "operator": "=",
                        "rhs": {
                            "type": "CONSTANT_VALUE",
                            "value": {
                                "type": "STRING",
                                "value": "hello",
                            },
                        },
                    },
                }
            ],
            "adornments": None,
            "attributes": [],
        },
        serialized_node,
        ignore_order=True,
    )


class IfElseGenericNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input

    class Ports(BaseNode.Ports):
        if_branch = Port.on_if(Inputs.input == "hello")
        else_branch = Port.on_else()


def test_serialize_node__if_else(serialize_node):
    serialized_node = serialize_node(IfElseGenericNode)
    assert not DeepDiff(
        {
            "id": "1f499f82-8cc0-4060-bf4d-d20ac409d4aa",
            "label": "IfElseGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "definition": {
                "name": "IfElseGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_ports_serialization",
                ],
                "bases": [{"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]}],
            },
            "trigger": {"id": "5b4f6553-69ca-4844-bbe4-9e5594bc8cae", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "3eeb7f03-7d65-45aa-b0e5-c7a453f5cbdf",
                    "type": "IF",
                },
                {
                    "id": "b8472c77-74d5-4432-bf8b-6cd65d3dde06",
                    "type": "ELSE",
                },
            ],
            "adornments": None,
            "attributes": [],
        },
        serialized_node,
        ignore_order=True,
    )


class IfElifElseGenericNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input

    class Ports(BaseNode.Ports):
        if_branch = Port.on_if(Inputs.input == "hello")
        elif_branch = Port.on_elif(Inputs.input == "world")
        else_branch = Port.on_else()


def test_serialize_node__if_elif_else(serialize_node):
    serialized_node = serialize_node(IfElifElseGenericNode)
    assert not DeepDiff(
        {
            "id": "21c49bfb-a90c-4565-a4e6-8eb5187e81ca",
            "label": "IfElifElseGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "definition": {
                "name": "IfElifElseGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_ports_serialization",
                ],
                "bases": [{"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]}],
            },
            "trigger": {"id": "22d55b5b-3545-4498-8658-9d0464202e78", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "f6e0a2c0-192d-452f-bde4-32fb938e91bc",
                    "type": "IF",
                },
                {
                    "id": "7e44de04-e816-4da8-9251-cf389442a5d6",
                    "type": "ELIF",
                },
                {
                    "id": "00db3698-ddf5-413b-8408-fff664c212d7",
                    "type": "ELSE",
                },
            ],
            "adornments": None,
            "attributes": [],
        },
        serialized_node,
        ignore_order=True,
    )
