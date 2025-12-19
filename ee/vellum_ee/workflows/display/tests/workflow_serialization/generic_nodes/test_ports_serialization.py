from uuid import uuid4
from typing import cast

from deepdiff import DeepDiff

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum_ee.workflows.display.base import WorkflowInputsDisplay, WorkflowMetaDisplay
from vellum_ee.workflows.display.editor.types import NodeDisplayData
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.exceptions import UnsupportedSerializationException
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


class Inputs(BaseInputs):
    input: str


def test_serialize_node__basic(serialize_node):
    class BasicGenericNode(BaseNode):
        pass

    serialized_node = serialize_node(BasicGenericNode)
    assert not DeepDiff(
        {
            "id": "7fc62d68-0a27-4506-b4ea-e40bc116c0c5",
            "label": "Basic Generic Node",
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
            "trigger": {"id": "454606d2-204a-4b29-b0dd-59233c9e5a0e", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "4173b79f-ebdd-4026-8046-01d20dcf2b13",
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


def test_serialize_node__if(serialize_node):
    class IfGenericNode(BaseNode):

        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(Inputs.input.equals("hello"))

    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=IfGenericNode, global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)}
    )

    assert not DeepDiff(
        {
            "id": "108e36a6-a773-4bc7-b6c4-38997e3690c5",
            "label": "If Generic Node",
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
            "trigger": {"id": "6769e811-fc56-4bab-9ebb-4b4b4b5ef023", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "cec9e02a-4097-4e0a-b62d-60da4f17db67",
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


def test_serialize_node__if_else(serialize_node):
    class IfElseGenericNode(BaseNode):

        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(Inputs.input.equals("hello"))
            else_branch = Port.on_else()

    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=IfElseGenericNode, global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)}
    )

    assert not DeepDiff(
        {
            "id": "6b16a6e3-cbe4-4672-b2bb-31ef930b0d97",
            "label": "If Else Generic Node",
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
            "trigger": {"id": "b4a3e968-0f88-457c-b91e-e6c490b669de", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "b3394650-f12e-443c-8abe-675bfb632cf5",
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
                    "id": "7c213f16-ae88-4080-8b44-2084d4280c3f",
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


def test_serialize_node__if_elif_else(serialize_node):
    class IfElifElseGenericNode(BaseNode):

        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(Inputs.input.equals("hello"))
            elif_branch = Port.on_elif(Inputs.input.equals("world"))
            else_branch = Port.on_else()

    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=IfElifElseGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    assert not DeepDiff(
        {
            "id": "da8860e8-e1ea-4e57-977b-7a8ef43415ee",
            "label": "If Elif Else Generic Node",
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
            "trigger": {"id": "1b86a845-df3a-4544-ae5b-a23887e735b1", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "d0fa9794-bd46-4238-b61f-6b03ba7053ba",
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
                    "id": "5b4afa12-5c0d-4e6a-b304-d56baf4738dc",
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
                    "id": "055fc9f8-3510-47d2-8dcf-d7bd0ea15fd6",
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


def test_serialize_node__node_output_reference(serialize_node):
    class NodeWithOutput(BaseNode):

        class Outputs(BaseNode.Outputs):
            output = Inputs.input

    class NodeWithOutputDisplay(BaseNodeDisplay[NodeWithOutput]):
        pass

    class GenericNodeReferencingOutput(BaseNode):

        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(NodeWithOutput.Outputs.output.equals("hello"))

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
            "trigger": {"id": "c43b6517-102a-44bc-83c8-37d42861d3e6", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "6258cb70-4cfc-4bc8-a26c-df14a50bc72a",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
                            "type": "NODE_OUTPUT",
                            "node_id": "242ad818-12ec-449f-87b4-d2bc513e2148",
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


def test_serialize_node__vellum_secret_reference(serialize_node):
    class GenericNodeReferencingSecret(BaseNode):

        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(VellumSecretReference(name="hello").equals("hello"))

    workflow_input_id = uuid4()
    serialized_node = serialize_node(
        node_class=GenericNodeReferencingSecret,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=workflow_input_id)},
    )

    assert not DeepDiff(
        {
            "id": "b1e770cb-31dd-461f-9041-8470c9f3e098",
            "label": "Generic Node Referencing Secret",
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
            "trigger": {"id": "96f50af1-8178-47b8-b8c0-97ca10e62845", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "aaad042f-02ce-400a-aad5-c9064925937b",
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


def test_serialize_node__execution_count_reference(serialize_node):
    class NodeWithExecutions(BaseNode):
        pass

    class NodeWithExecutionsDisplay(BaseNodeDisplay[NodeWithExecutions]):
        pass

    class GenericNodeReferencingExecutions(BaseNode):

        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(NodeWithExecutions.Execution.count.equals(5))

    workflow_input_id = uuid4()
    serialized_node = serialize_node(
        node_class=GenericNodeReferencingExecutions,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=workflow_input_id)},
        global_node_displays={NodeWithExecutions: NodeWithExecutionsDisplay()},
    )

    assert not DeepDiff(
        {
            "id": "5e6512c2-7a97-4b44-abed-64cee4388df5",
            "label": "Generic Node Referencing Executions",
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
            "trigger": {"id": "4a120ba5-2384-4854-a9fb-b9fe68bcd52a", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "575af12c-c700-438c-9123-198cca866535",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
                            "type": "EXECUTION_COUNTER",
                            "node_id": "075e9647-b657-4a6e-ab21-c3a7f1a68ada",
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


def test_serialize_node__null(serialize_node):
    class NullGenericNode(BaseNode):

        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(Inputs.input.is_null())

    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=NullGenericNode, global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)}
    )

    assert not DeepDiff(
        {
            "id": "05d96ec5-4a05-43ca-a1c2-e92a49ac9520",
            "label": "Null Generic Node",
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
            "trigger": {"id": "bc28e72e-b75b-487c-8b8f-345c062d848d", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "b0b5f49f-7d02-4b45-9c8b-b4b5440a0e8e",
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


def test_serialize_node__between(serialize_node):
    class IntegerInputs(BaseInputs):
        input: int

    class BetweenGenericNode(BaseNode):

        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(IntegerInputs.input.between(1, 10))

    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=BetweenGenericNode,
        global_workflow_input_displays={IntegerInputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    assert not DeepDiff(
        {
            "id": "f32ab40b-7de2-4dc4-b5ef-41a753bf8bb4",
            "label": "Between Generic Node",
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
            "trigger": {"id": "99c92fd8-66af-4910-8f1c-773fa4c7fc42", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "9894ea65-ecbd-4d31-9ede-b65debebc908",
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


def test_serialize_node__or(serialize_node):
    class OrGenericNode(BaseNode):

        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(Inputs.input.equals("hello") | Inputs.input.equals("world"))

    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=OrGenericNode, global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)}
    )

    assert not DeepDiff(
        {
            "id": "8971f041-6b61-4d02-b02b-9d221f224ea2",
            "label": "Or Generic Node",
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
            "trigger": {"id": "69c1fb9e-2b89-46f2-a1b0-c7bd2e55d812", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "0306137d-1af9-430e-8582-08054d1ed350",
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


def test_serialize_node__and_then_or(serialize_node):
    class AndThenOrGenericNode(BaseNode):

        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(
                Inputs.input.equals("hello") & Inputs.input.equals("then") | Inputs.input.equals("world")
            )

    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=AndThenOrGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    assert not DeepDiff(
        {
            "id": "ce9daa70-0e06-4ee4-b611-cd5702e92eed",
            "label": "And Then Or Generic Node",
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
            "trigger": {"id": "eddecfb5-4bdf-4193-b8c2-bc7bf1bd96b1", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "c87cfe7b-a6a9-43eb-a890-4785ee1783e7",
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


def test_serialize_node__parenthesized_and_then_or(serialize_node):
    class ParenthesizedAndThenOrGenericNode(BaseNode):

        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(
                Inputs.input.equals("hello") & (Inputs.input.equals("then") | Inputs.input.equals("world"))
            )

    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=ParenthesizedAndThenOrGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    assert not DeepDiff(
        {
            "id": "c311e689-f06c-47a9-88dc-ca2e1f0ae455",
            "label": "Parenthesized And Then Or Generic Node",
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
            "trigger": {"id": "3d9cd609-7801-4ce5-b70c-2afcc88d8af3", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "b58e5bcb-cfcd-4249-b80d-447dc4b096f0",
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


def test_serialize_node__or_then_and(serialize_node):
    class OrThenAndGenericNode(BaseNode):

        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(
                Inputs.input.equals("hello") | Inputs.input.equals("then") & Inputs.input.equals("world")
            )

    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=OrThenAndGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    assert not DeepDiff(
        {
            "id": "4394a83e-897c-4fe1-a76c-6e8853a619a9",
            "label": "Or Then And Generic Node",
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
            "trigger": {"id": "ef0b522b-f9c0-4767-b7ea-f0fb15b213ed", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "2770f76e-f20e-40c6-86a0-8efbc08a8265",
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


def test_serialize_node__blank(serialize_node):
    """
    Tests that a node with an is_blank() port condition serializes correctly.
    """

    # GIVEN a node with an is_blank() port condition
    class BlankGenericNode(BaseNode):

        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(Inputs.input.is_blank())

    input_id = uuid4()

    # WHEN we serialize the node
    serialized_node = serialize_node(
        node_class=BlankGenericNode, global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)}
    )

    # THEN the serialized node should have the correct structure with a UNARY_EXPRESSION and "blank" operator
    assert not DeepDiff(
        {
            "id": "a9067b0e-6c3b-4ed0-8b0a-a4eb861f75a8",
            "label": "Blank Generic Node",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "BlankGenericNode",
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
            "trigger": {"id": "f4cc239d-9feb-4eeb-84d9-62633a7883e7", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "3ac47591-d4dc-470b-be44-74e1445518e2",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "UNARY_EXPRESSION",
                        "lhs": {
                            "type": "WORKFLOW_INPUT",
                            "input_variable_id": str(input_id),
                        },
                        "operator": "blank",
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


def test_serialize_node__not_blank(serialize_node):
    """
    Tests that a node with an is_not_blank() port condition serializes correctly.
    """

    # GIVEN a node with an is_not_blank() port condition
    class NotBlankGenericNode(BaseNode):

        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(Inputs.input.is_not_blank())

    input_id = uuid4()

    # WHEN we serialize the node
    serialized_node = serialize_node(
        node_class=NotBlankGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    # THEN the serialized node should have the correct structure with a UNARY_EXPRESSION and "notBlank" operator
    assert not DeepDiff(
        {
            "id": "a9349004-bd02-458e-af66-7b515cdd4d3a",
            "label": "Not Blank Generic Node",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "NotBlankGenericNode",
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
            "trigger": {"id": "60521d64-adc6-4f49-8605-0bf617a23a2d", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "4824d11b-9d44-4183-8e7f-c4eb21262cc8",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "UNARY_EXPRESSION",
                        "lhs": {
                            "type": "WORKFLOW_INPUT",
                            "input_variable_id": str(input_id),
                        },
                        "operator": "notBlank",
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


def test_serialize_node__parse_json(serialize_node):

    class ParseJsonGenericNode(BaseNode):

        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(Inputs.input.parse_json().equals({"key": "value"}))

    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=ParseJsonGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    assert not DeepDiff(
        {
            "id": "60a14037-a8cf-47ad-b34b-47ec9dbf9715",
            "label": "Parse Json Generic Node",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "ParseJsonGenericNode",
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
            "trigger": {"id": "2d711e0e-7b50-4eaf-ad2c-f6d7441b75f0", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "9eedb158-20a0-456e-b436-d9a7460b791e",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
                            "type": "UNARY_EXPRESSION",
                            "lhs": {
                                "type": "WORKFLOW_INPUT",
                                "input_variable_id": str(input_id),
                            },
                            "operator": "parseJson",
                        },
                        "operator": "=",
                        "rhs": {
                            "type": "CONSTANT_VALUE",
                            "value": {
                                "type": "JSON",
                                "value": {"key": "value"},
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


def test_serialize_node__unsupported_descriptor_type():
    """
    Tests that serializing a generic node with an unsupported descriptor type
    returns the node with an empty expression and adds the error to the display context.
    """

    # GIVEN a custom descriptor that is not a supported expression type
    class UnsupportedDescriptor(BaseDescriptor[bool]):
        def __init__(self) -> None:
            super().__init__(name="unsupported", types=(bool,), instance=None)

    # AND a generic node that uses this unsupported descriptor in a port condition
    class UnsupportedDescriptorNode(BaseNode):
        class Ports(BaseNode.Ports):
            if_branch = Port.on_if(UnsupportedDescriptor())

    # AND a display context with dry_run=True to capture errors
    node_display_class = get_node_display_class(UnsupportedDescriptorNode)
    node_display = node_display_class()

    context = WorkflowDisplayContext(
        workflow_display_class=BaseWorkflowDisplay,
        workflow_display=WorkflowMetaDisplay(
            entrypoint_node_id=uuid4(),
            entrypoint_node_source_handle_id=uuid4(),
            entrypoint_node_display=NodeDisplayData(),
        ),
        node_displays={UnsupportedDescriptorNode: node_display},
        dry_run=True,
    )

    # WHEN we serialize the node
    serialized_node = node_display.serialize(context)

    # THEN the node should still be returned
    assert serialized_node["type"] == "GENERIC"

    # AND the port should have a None expression
    ports = cast(JsonArray, serialized_node["ports"])
    assert len(ports) == 1
    port = cast(JsonObject, ports[0])
    assert port["type"] == "IF"
    assert port["expression"] is None

    # AND the error should be added to the display context
    errors = list(context.errors)
    assert len(errors) == 1
    assert isinstance(errors[0], UnsupportedSerializationException)
    assert "Unsupported condition type" in str(errors[0])
