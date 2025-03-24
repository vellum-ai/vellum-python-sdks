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


def test_serialize_node__basic(serialize_node):
    class BasicGenericNode(BaseNode):
        pass

    serialized_node = serialize_node(BasicGenericNode)

    assert not DeepDiff(
        {
            "id": "8d7cbfe4-72ca-4367-a401-8d28723d2f00",
            "label": "test_serialize_node__basic.<locals>.BasicGenericNode",
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
            "trigger": {"id": "b95cca96-b570-42ac-ace8-51ca0f627881", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "8bec8d0c-113f-4110-afcb-4a6e566e7236",
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
            "id": "bba4b15a-dea0-48c9-a79b-4e12e99db00f",
            "label": "test_serialize_node__if.<locals>.IfGenericNode",
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
            "trigger": {"id": "46e21bcc-47e1-457f-8134-ead575253b74", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "9889fe69-62f8-4bb3-aac6-425b75700bea",
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
            "id": "25c9c3f1-4014-47ac-90cf-5216de10d05c",
            "label": "test_serialize_node__if_else.<locals>.IfElseGenericNode",
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
            "trigger": {"id": "664c941c-275c-474c-9a5c-8501b934e86d", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "6fd9edea-9c1f-4463-aeb9-bfdde3231ee0",
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
                    "id": "7f9ea016-22da-49b3-be46-b80fb96beedf",
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
            "id": "7b2b9cfc-12aa-432c-940d-cbe53e71de9c",
            "label": "test_serialize_node__if_elif_else.<locals>.IfElifElseGenericNode",
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
            "trigger": {"id": "bba33909-beeb-4ebd-ad77-46b617ab07b0", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "19a1cc62-1f18-49b0-8026-7c82709e34db",
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
                    "id": "dc0b680e-d7b3-4a44-a37d-df22b310bda3",
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
                    "id": "16d0b698-1353-4eb3-9768-4a6e5ed4b1da",
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
            NodeWithOutput.Outputs.output: (NodeWithOutput, NodeOutputDisplay(id=node_output_id, name="output"))
        },
    )

    assert not DeepDiff(
        {
            "id": "ac067acc-6a6f-44b1-ae84-428e965ce691",
            "label": "test_serialize_node__node_output_reference.<locals>.GenericNodeReferencingOutput",
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
            "trigger": {"id": "c8804b97-9f84-41b6-ade8-aa74544d6846", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "500075dc-fc65-428a-b3c0-a410f8c7f8cf",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
                            "type": "NODE_OUTPUT",
                            "node_id": "21213d1e-991c-405a-b4fa-a1e01c4dd088",
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
            "id": "feb4b331-e25f-4a5c-9840-c5575b1efd5c",
            "label": "test_serialize_node__vellum_secret_reference.<locals>.GenericNodeReferencingSecret",
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
            "trigger": {"id": "93cc612b-c020-420b-94ef-62d9687c212c", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "3b6b4048-8622-446d-9772-2766357d7b18",
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
            "id": "0b4fe8a6-6d0c-464e-9372-10110e2b0e13",
            "label": "test_serialize_node__execution_count_reference.<locals>.GenericNodeReferencingExecutions",
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
            "trigger": {"id": "ccc61dda-a947-47ac-b484-78f971ae1148", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "79d0cfa3-c8f9-4434-a2f8-5e416d66437a",
                    "type": "IF",
                    "name": "if_branch",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
                            "type": "EXECUTION_COUNTER",
                            "node_id": "235c66f9-c76b-4df0-9bff-cfba2ef1ad18",
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
            "id": "1838ce1f-9c07-4fd0-9fd4-2a3a841ea402",
            "label": "test_serialize_node__null.<locals>.NullGenericNode",
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
            "trigger": {"id": "ad543514-516f-47ac-a363-1bbfccb0dfa9", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "7f1fb75d-0c8b-4ebc-8c59-4ae68f1a68e1",
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
            "id": "f2f5a1f2-a12d-4ce0-bfe9-42190ffe5328",
            "label": "test_serialize_node__between.<locals>.BetweenGenericNode",
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
            "trigger": {"id": "36799ad9-5c1a-4bb6-be13-aee5487c021b", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "b745c089-1023-46dc-b2b6-ba75ac37563a",
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
            "id": "5386abad-3378-4378-b3a8-831b4b77dc23",
            "label": "test_serialize_node__or.<locals>.OrGenericNode",
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
            "trigger": {"id": "f2837ac2-2132-4af2-b8bb-30de9b0a2815", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "0bd64819-b866-4333-82e0-8ac672c09b79",
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
            "id": "4d3995b1-437b-48d9-8878-9f57a8b725f1",
            "label": "test_serialize_node__and_then_or.<locals>.AndThenOrGenericNode",
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
            "trigger": {"id": "aa7747fe-4b59-4994-a5c4-0ccc8065f93d", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "8bb89da2-a752-4541-8f90-1276c44910a8",
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
            "id": "223864c9-0088-4c05-9b7d-e5b1c9ec936d",
            "label": "test_serialize_node__parenthesized_and_then_or.<locals>.ParenthesizedAndThenOrGenericNode",
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
            "trigger": {"id": "71601746-3722-423c-8fc0-d15a6bb6ddd4", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "30478083-924d-469e-ad55-df28bc282cdb",
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
            "id": "a946342e-4ede-4e96-8e3d-f396748d9f7c",
            "label": "test_serialize_node__or_then_and.<locals>.OrThenAndGenericNode",
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
            "trigger": {"id": "9c875b19-fce1-4eef-80ea-19651dec1a76", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "7f442cce-0b99-482c-aec8-8eed6ccadde2",
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
            "id": "bfc3f81b-242a-4f43-9e1c-648223d77768",
            "label": "test_serialize_node__parse_json.<locals>.ParseJsonGenericNode",
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
            "trigger": {"id": "ecff8eef-b928-48e7-ac26-841322ff2752", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "5a88bac8-89b3-4d81-b539-2f977a36a9c0",
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
