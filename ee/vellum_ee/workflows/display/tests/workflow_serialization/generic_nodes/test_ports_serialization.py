from uuid import uuid4

from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum_ee.workflows.display.base import WorkflowInputsDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.nodes.vellum.base_node import BaseNodeDisplay


class Inputs(BaseInputs):
    input: str


class BasicGenericNode(BaseNode):
    pass


def test_serialize_node__basic(serialize_node):
    serialized_node = serialize_node(BasicGenericNode)
    assert not DeepDiff(
        {
            "id": "c2ed23f7-f6cb-4a56-a91c-2e5f9d8fda7f",
            "label": "BasicGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
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
            },
            "trigger": {"id": "9d3a1b3d-4a38-4f2e-bbf1-dd8be152bce8", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "4fbf0fff-a42e-4410-852a-238b5059198e",
                    "name": "default",
                    "type": "DEFAULT",
                }
            ],
            "adornments": None,
            "attributes": [],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


class IfGenericNode(BaseNode):
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
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
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
            },
            "trigger": {"id": "a8afaebc-7333-4e3f-b221-24452b4a1d47", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "7605b4c0-a432-4517-b759-5858045a5146",
                    "type": "IF",
                    "name": "if_branch",
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
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


class IfElseGenericNode(BaseNode):
    class Ports(BaseNode.Ports):
        if_branch = Port.on_if(Inputs.input.equals("hello"))
        else_branch = Port.on_else()


def test_serialize_node__if_else(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=IfElseGenericNode, global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)}
    )

    assert not DeepDiff(
        {
            "id": "1f499f82-8cc0-4060-bf4d-d20ac409d4aa",
            "label": "IfElseGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
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
            },
            "trigger": {"id": "5b4f6553-69ca-4844-bbe4-9e5594bc8cae", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "3eeb7f03-7d65-45aa-b0e5-c7a453f5cbdf",
                    "type": "IF",
                    "name": "if_branch",
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
                },
                {
                    "id": "b8472c77-74d5-4432-bf8b-6cd65d3dde06",
                    "type": "ELSE",
                    "name": "else_branch",
                    "expression": None,
                },
            ],
            "adornments": None,
            "attributes": [],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


class IfElifElseGenericNode(BaseNode):
    class Ports(BaseNode.Ports):
        if_branch = Port.on_if(Inputs.input.equals("hello"))
        elif_branch = Port.on_elif(Inputs.input.equals("world"))
        else_branch = Port.on_else()


def test_serialize_node__if_elif_else(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=IfElifElseGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )
    assert not DeepDiff(
        {
            "id": "21c49bfb-a90c-4565-a4e6-8eb5187e81ca",
            "label": "IfElifElseGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
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
            },
            "trigger": {"id": "22d55b5b-3545-4498-8658-9d0464202e78", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "f6e0a2c0-192d-452f-bde4-32fb938e91bc",
                    "type": "IF",
                    "name": "if_branch",
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
                },
                {
                    "id": "7e44de04-e816-4da8-9251-cf389442a5d6",
                    "type": "ELIF",
                    "name": "elif_branch",
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
                                "value": "world",
                            },
                        },
                    },
                },
                {
                    "id": "00db3698-ddf5-413b-8408-fff664c212d7",
                    "type": "ELSE",
                    "expression": None,
                    "name": "else_branch",
                },
            ],
            "adornments": None,
            "attributes": [],
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
    class Ports(BaseNode.Ports):
        if_branch = Port.on_if(NodeWithOutput.Outputs.output.equals("hello"))


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
            "definition": {
                "name": "GenericNodeReferencingOutput",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_ports_serialization",
                ],
            },
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "trigger": {"id": "449072ba-f7b6-4314-ac96-682123f225e5", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "ec9a79b8-65c3-4de8-bd29-42c914d72d4f",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
                            "type": "NODE_OUTPUT",
                            "node_id": "cd954d76-0b0a-4d9b-9bdf-347179c38cb6",
                            "node_output_id": str(node_output_id),
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
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


class GenericNodeReferencingSecret(BaseNode):
    class Ports(BaseNode.Ports):
        if_branch = Port.on_if(VellumSecretReference(name="hello").equals("hello"))


def test_serialize_node__vellum_secret_reference(serialize_node):
    workflow_input_id = uuid4()
    serialized_node = serialize_node(
        node_class=GenericNodeReferencingSecret,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=workflow_input_id)},
    )

    assert not DeepDiff(
        {
            "id": "88272edd-fc81-403b-bb87-a116ef8f269e",
            "label": "GenericNodeReferencingSecret",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "definition": {
                "name": "GenericNodeReferencingSecret",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_ports_serialization",
                ],
            },
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "trigger": {"id": "2709539b-352d-455a-bb86-dba070b59aa1", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "a353d3f6-2a1f-457c-b8d1-13db5b45be8f",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {"type": "VELLUM_SECRET", "vellum_secret_name": "hello"},
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
    class Ports(BaseNode.Ports):
        if_branch = Port.on_if(NodeWithExecutions.Execution.count.equals(5))


def test_serialize_node__execution_count_reference(serialize_node):
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
            "definition": {
                "name": "GenericNodeReferencingExecutions",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_ports_serialization",
                ],
            },
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "trigger": {"id": "68a91426-4c30-4194-a4c0-cff224d3c0f3", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "1794c2eb-5cab-49fe-9354-dfc29f11b374",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
                            "type": "EXECUTION_COUNTER",
                            "node_id": "c09bd5a6-dc04-4036-90d4-580acd43c71f",
                        },
                        "operator": "=",
                        "rhs": {
                            "type": "CONSTANT_VALUE",
                            "value": {
                                "type": "NUMBER",
                                "value": 5,
                            },
                        },
                    },
                }
            ],
            "adornments": None,
            "attributes": [],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


class NullGenericNode(BaseNode):
    class Ports(BaseNode.Ports):
        if_branch = Port.on_if(Inputs.input.is_null())


def test_serialize_node__null(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=NullGenericNode, global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)}
    )

    assert not DeepDiff(
        {
            "id": "d5fe72cd-a2bd-4f91-ae13-44e4c617815e",
            "label": "NullGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "NullGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_ports_serialization",
                ],
            },
            "trigger": {"id": "26b257ed-6a7d-4ca3-a5c8-d17ba1e776ba", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "51932d23-492e-4b3b-8b03-6ad7303a80c9",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "UNARY_EXPRESSION",
                        "lhs": {
                            "type": "WORKFLOW_INPUT",
                            "input_variable_id": str(input_id),
                        },
                        "operator": "null",
                    },
                }
            ],
            "adornments": None,
            "attributes": [],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


class IntegerInputs(BaseInputs):
    input: int


class BetweenGenericNode(BaseNode):
    class Ports(BaseNode.Ports):
        if_branch = Port.on_if(IntegerInputs.input.between(1, 10))


def test_serialize_node__between(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=BetweenGenericNode,
        global_workflow_input_displays={IntegerInputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    assert not DeepDiff(
        {
            "id": "3ef33a2a-6ad5-415c-be75-f38cc1403dfc",
            "label": "BetweenGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "BetweenGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_ports_serialization",
                ],
            },
            "trigger": {"id": "086a355e-d9ef-4039-af35-9f1211497b32", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "a86bd19f-a9f7-45c3-80ff-73330b1b75af",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "TERNARY_EXPRESSION",
                        "base": {
                            "type": "WORKFLOW_INPUT",
                            "input_variable_id": str(input_id),
                        },
                        "operator": "between",
                        "lhs": {
                            "type": "CONSTANT_VALUE",
                            "value": {
                                "type": "NUMBER",
                                "value": 1,
                            },
                        },
                        "rhs": {
                            "type": "CONSTANT_VALUE",
                            "value": {
                                "type": "NUMBER",
                                "value": 10,
                            },
                        },
                    },
                }
            ],
            "adornments": None,
            "attributes": [],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


class OrGenericNode(BaseNode):
    class Ports(BaseNode.Ports):
        if_branch = Port.on_if(Inputs.input.equals("hello") | Inputs.input.equals("world"))


def test_serialize_node__or(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=OrGenericNode, global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)}
    )

    assert not DeepDiff(
        {
            "id": "63900268-b9d0-4285-8ea4-7c478f4abf88",
            "label": "OrGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "OrGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_ports_serialization",
                ],
            },
            "trigger": {"id": "dc245f37-9be7-4097-a50a-4f7196e24313", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "652a42f9-f4e7-4791-8167-8903ff839520",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
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
                        "operator": "or",
                        "rhs": {
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
                                    "value": "world",
                                },
                            },
                        },
                    },
                }
            ],
            "adornments": None,
            "attributes": [],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


class AndThenOrGenericNode(BaseNode):
    class Ports(BaseNode.Ports):
        if_branch = Port.on_if(
            Inputs.input.equals("hello") & Inputs.input.equals("then") | Inputs.input.equals("world")
        )


def test_serialize_node__and_then_or(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=AndThenOrGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    assert not DeepDiff(
        {
            "id": "b3908206-e540-4dac-9c64-a2e12b847b15",
            "label": "AndThenOrGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "AndThenOrGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_ports_serialization",
                ],
            },
            "trigger": {"id": "33cfa8f4-bfc5-40b3-8df8-ab86371c26e0", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "42c89e95-6bbf-4e85-8f26-d4b6fc55d99c",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
                            "type": "BINARY_EXPRESSION",
                            "lhs": {
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
                            "operator": "and",
                            "rhs": {
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
                                        "value": "then",
                                    },
                                },
                            },
                        },
                        "operator": "or",
                        "rhs": {
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
                                    "value": "world",
                                },
                            },
                        },
                    },
                }
            ],
            "adornments": None,
            "attributes": [],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


class ParenthesizedAndThenOrGenericNode(BaseNode):
    class Ports(BaseNode.Ports):
        if_branch = Port.on_if(
            Inputs.input.equals("hello") & (Inputs.input.equals("then") | Inputs.input.equals("world"))
        )


def test_serialize_node__parenthesized_and_then_or(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=ParenthesizedAndThenOrGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    assert not DeepDiff(
        {
            "id": "6ed0373a-13b1-4edb-b0c4-31642cf312f8",
            "label": "ParenthesizedAndThenOrGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "ParenthesizedAndThenOrGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_ports_serialization",
                ],
            },
            "trigger": {"id": "91ac3b05-c931-4a4c-bb48-c2ba0e883867", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "cc07394b-f20b-4370-8a5b-af90e847a73f",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
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
                        "operator": "and",
                        "rhs": {
                            "type": "BINARY_EXPRESSION",
                            "lhs": {
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
                                        "value": "then",
                                    },
                                },
                            },
                            "operator": "or",
                            "rhs": {
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
                                        "value": "world",
                                    },
                                },
                            },
                        },
                    },
                }
            ],
            "adornments": None,
            "attributes": [],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


class OrThenAndGenericNode(BaseNode):
    class Ports(BaseNode.Ports):
        if_branch = Port.on_if(
            Inputs.input.equals("hello") | Inputs.input.equals("then") & Inputs.input.equals("world")
        )


def test_serialize_node__or_then_and(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=OrThenAndGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    assert not DeepDiff(
        {
            "id": "a0e0a35b-132e-4168-ad7d-ceb04f3203f2",
            "label": "OrThenAndGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "OrThenAndGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_ports_serialization",
                ],
            },
            "trigger": {"id": "dfa53d32-36cc-4b1d-adad-d4de21ac1e5a", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "daaff604-da1e-45e6-b3df-5bc8de8d55fe",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
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
                        "operator": "or",
                        "rhs": {
                            "type": "BINARY_EXPRESSION",
                            "lhs": {
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
                                        "value": "then",
                                    },
                                },
                            },
                            "operator": "and",
                            "rhs": {
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
                                        "value": "world",
                                    },
                                },
                            },
                        },
                    },
                }
            ],
            "adornments": None,
            "attributes": [],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )
