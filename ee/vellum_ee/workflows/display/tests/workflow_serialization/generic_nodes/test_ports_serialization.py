from uuid import uuid4

from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum_ee.workflows.display.base import WorkflowInputsDisplay
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay


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
            "trigger": {"id": "9d3a1b3d-4a38-4f2e-bbf1-dd8be152bce8", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "89dccfa5-cc1a-4612-bd87-86cb444f6dd4",
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
            "trigger": {"id": "a8afaebc-7333-4e3f-b221-24452b4a1d47", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "d713e346-b55a-4871-91de-f1470bfb3479",
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
            "trigger": {"id": "5b4f6553-69ca-4844-bbe4-9e5594bc8cae", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "1b02eabf-f2bd-45bd-ab26-fe4034ed5978",
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
                    "id": "2c858834-8f65-4b6b-89d8-07b394764666",
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
            "trigger": {"id": "22d55b5b-3545-4498-8658-9d0464202e78", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "dcaa1d8e-01c6-48b4-a851-8828b49d0f57",
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
                    "id": "e00351f8-f1f9-4f7b-bf7a-c24e3db40d6c",
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
                    "id": "90caeb67-5ab7-46aa-b65e-01c27f549eed",
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
            "trigger": {"id": "449072ba-f7b6-4314-ac96-682123f225e5", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "eecccf2b-82af-4559-8a1b-0c5de5890ac2",
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
            "trigger": {"id": "2709539b-352d-455a-bb86-dba070b59aa1", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "b6387c9c-2cce-4667-9567-97e433503e72",
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
            "trigger": {"id": "68a91426-4c30-4194-a4c0-cff224d3c0f3", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "13ab561e-09c9-48ed-b22b-a4de4d9df887",
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
                                "value": 5.0,
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
            "trigger": {"id": "26b257ed-6a7d-4ca3-a5c8-d17ba1e776ba", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "76a2867d-dd4c-409c-b97f-94b168a2233a",
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
            "trigger": {"id": "086a355e-d9ef-4039-af35-9f1211497b32", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "71493245-0778-46f2-8bda-863af50d910d",
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
                                "value": 1.0,
                            },
                        },
                        "rhs": {
                            "type": "CONSTANT_VALUE",
                            "value": {
                                "type": "NUMBER",
                                "value": 10.0,
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
            "trigger": {"id": "dc245f37-9be7-4097-a50a-4f7196e24313", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "9b4511aa-2d57-44f9-8156-d41dd8b5f98e",
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
            "trigger": {"id": "33cfa8f4-bfc5-40b3-8df8-ab86371c26e0", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "91174ae5-6ce0-4f6c-9c05-ecfbfb4058f6",
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
            "trigger": {"id": "91ac3b05-c931-4a4c-bb48-c2ba0e883867", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "915f923b-f398-48af-93a4-5f7e66b8aa76",
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
            "trigger": {"id": "dfa53d32-36cc-4b1d-adad-d4de21ac1e5a", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "413bba3d-6a16-4f96-ba45-b5372f819277",
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
