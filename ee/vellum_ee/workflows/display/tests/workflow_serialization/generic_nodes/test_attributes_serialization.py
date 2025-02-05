from uuid import uuid4

from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.base import WorkflowInputsDisplay
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


class Inputs(BaseInputs):
    input: str


class ConstantValueGenericNode(BaseNode):
    attr: str = "hello"


def test_serialize_node__constant_value(serialize_node):
    serialized_node = serialize_node(ConstantValueGenericNode)

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
            "trigger": {"id": "279e8228-9b82-43a3-8c31-affc036e3a0b", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "7cd373aa-34d1-402d-bcb4-1c8f329b63e9", "type": "DEFAULT", "name": "default"}],
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


class ConstantValueReferenceGenericNode(BaseNode):
    attr: str = ConstantValueReference("hello")


def test_serialize_node__constant_value_reference(serialize_node):
    serialized_node = serialize_node(ConstantValueReferenceGenericNode)

    assert not DeepDiff(
        {
            "id": "9271e2b1-f47e-47a4-95ae-51299dedb62f",
            "label": "ConstantValueReferenceGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "ConstantValueReferenceGenericNode",
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
            "trigger": {"id": "8cc0b4c4-4ae4-4248-8fd5-bfb2e658eb51", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "fe696d84-47c2-4325-8020-34a1c586a759", "name": "default", "type": "DEFAULT"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "460aeb68-7369-43d2-9d3d-37caa425611f",
                    "name": "attr",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "hello"}},
                }
            ],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


class LazyReferenceGenericNode(BaseNode):
    attr: str = LazyReference(lambda: ConstantValueReference("hello"))


def test_serialize_node__lazy_reference(serialize_node):
    serialized_node = serialize_node(LazyReferenceGenericNode)

    assert not DeepDiff(
        {
            "id": "29563b11-bd4d-47b0-b017-372f78aeaef5",
            "label": "LazyReferenceGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "LazyReferenceGenericNode",
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
            "trigger": {"id": "56e9791a-078a-4bb7-90bc-a26c3991c70f", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "acb761a0-fcc2-4d21-bc8c-d0d560912c04", "name": "default", "type": "DEFAULT"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "4370b381-9165-4fb4-881e-480507abe069",
                    "name": "attr",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "hello"}},
                }
            ],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


def test_serialize_node__lazy_reference_with_string():
    # GIVEN two nodes with one lazily referencing the other
    class LazyReferenceGenericNode(BaseNode):
        attr = LazyReference[str]("OtherNode.Outputs.result")

    class OtherNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    # AND a workflow with both nodes
    class Workflow(BaseWorkflow):
        graph = LazyReferenceGenericNode >> OtherNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(base_display_class=VellumWorkflowDisplay, workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the attribute reference
    lazy_reference_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(LazyReferenceGenericNode.__id__)
    )

    assert lazy_reference_node["attributes"] == [
        {
            "id": "98833d71-42a8-47e9-81c4-6a35646e3d3c",
            "name": "attr",
            "value": {
                "type": "NODE_OUTPUT",
                "node_id": str(OtherNode.__id__),
                "node_output_id": "7a3406a1-6f11-4568-8aa0-e5dba6534dc2",
            },
        }
    ]


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
            "trigger": {"id": "b1a5d749-bac0-4f11-8427-191febb2198e", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "d15c7175-139c-4885-8ef8-3e4081db121b", "type": "DEFAULT", "name": "default"}],
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
            "trigger": {"id": "449072ba-f7b6-4314-ac96-682123f225e5", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "1879f33e-6efa-46a0-9281-e02bbbc1d413", "type": "DEFAULT", "name": "default"}],
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
            "trigger": {"id": "3ea0305d-d8ea-45fe-8cf1-f6c1c85e6979", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "881abc1c-ada3-4405-8faf-e167fa2f851b", "type": "DEFAULT", "name": "default"}],
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
            "trigger": {"id": "68a91426-4c30-4194-a4c0-cff224d3c0f3", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "0e1f78d5-8be1-4533-b2b4-a52777a8d43d", "type": "DEFAULT", "name": "default"}],
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


class CoalesceNodeA(BaseNode):
    class Outputs(BaseNode.Outputs):
        output: str


class CoalesceNodeADisplay(BaseNodeDisplay[CoalesceNodeA]):
    pass


class CoalesceNodeB(BaseNode):
    class Outputs(BaseNode.Outputs):
        output: str


class CoalesceNodeBDisplay(BaseNodeDisplay[CoalesceNodeB]):
    pass


class CoalesceNodeFinal(BaseNode):
    attr = CoalesceNodeA.Outputs.output.coalesce(CoalesceNodeB.Outputs.output)


class CoalesceNodeFinalDisplay(BaseNodeDisplay[CoalesceNodeFinal]):
    pass


def test_serialize_node__coalesce(serialize_node):
    coalesce_node_a_output_id = uuid4()
    coalesce_node_b_output_id = uuid4()
    serialized_node = serialize_node(
        node_class=CoalesceNodeFinal,
        global_node_displays={
            CoalesceNodeA: CoalesceNodeADisplay(),
            CoalesceNodeB: CoalesceNodeBDisplay(),
            CoalesceNodeFinal: CoalesceNodeFinalDisplay(),
        },
        global_node_output_displays={
            CoalesceNodeA.Outputs.output: (
                CoalesceNodeA,
                NodeOutputDisplay(id=coalesce_node_a_output_id, name="output"),
            ),
            CoalesceNodeB.Outputs.output: (
                CoalesceNodeB,
                NodeOutputDisplay(id=coalesce_node_b_output_id, name="output"),
            ),
        },
    )

    assert not DeepDiff(
        {
            "id": "84d0ce62-afd1-4186-b0e3-5dd8e5ca8b65",
            "label": "CoalesceNodeFinal",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "CoalesceNodeFinal",
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
            "trigger": {"id": "5165f887-153b-4ecd-9219-1beb3cf4f906", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "08ab456d-f541-4400-8305-e97f30cbe745", "name": "default", "type": "DEFAULT"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "5a22dd48-9ef3-456b-85b8-7662cf7823eb",
                    "name": "attr",
                    "value": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
                            "type": "NODE_OUTPUT",
                            "node_id": "20c340f2-409c-4d31-b44b-eeffd76938d5",
                            "node_output_id": str(coalesce_node_a_output_id),
                        },
                        "operator": "coalesce",
                        "rhs": {
                            "type": "NODE_OUTPUT",
                            "node_id": "9fac3c54-4e75-46ca-a1f2-a80fc6d8ad3f",
                            "node_output_id": str(coalesce_node_b_output_id),
                        },
                    },
                }
            ],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )
