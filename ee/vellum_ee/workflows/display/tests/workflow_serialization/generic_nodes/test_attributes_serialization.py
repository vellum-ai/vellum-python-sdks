import pytest
from uuid import uuid4
from typing import List

from deepdiff import DeepDiff

from vellum.client.types.chat_message import ChatMessage
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.base import WorkflowInputsDisplay
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


class Inputs(BaseInputs):
    input: str


def test_serialize_node__constant_value(serialize_node):
    class ConstantValueGenericNode(BaseNode):
        attr: str = "hello"

    serialized_node = serialize_node(ConstantValueGenericNode)

    assert not DeepDiff(
        {
            "id": "67e07859-7f67-4287-9854-06ab4199e576",
            "label": "test_serialize_node__constant_value.<locals>.ConstantValueGenericNode",
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
            "trigger": {"id": "e2cde904-de60-4755-87cf-55052ea23a51", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "96ac6512-0128-4cf7-ba51-2725b4807c8f", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "84e4f91c-af1a-4f9d-a578-e3f234dea23b",
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


def test_serialize_node__constant_value_reference(serialize_node):
    class ConstantValueReferenceGenericNode(BaseNode):
        attr: str = ConstantValueReference("hello")

    serialized_node = serialize_node(ConstantValueReferenceGenericNode)

    assert not DeepDiff(
        {
            "id": "73643f17-e49e-47d2-bd01-bb9c3eab6ae9",
            "label": "test_serialize_node__constant_value_reference.<locals>.ConstantValueReferenceGenericNode",
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
            "trigger": {"id": "dc2f90b9-14a1-457a-a9f9-dec7a04f74eb", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "61adfacf-c3a9-4aea-a3da-bcdbc03273c6", "name": "default", "type": "DEFAULT"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "f8e5efc6-8117-4a1c-bcea-5ba23555409a",
                    "name": "attr",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "hello"}},
                }
            ],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


def test_serialize_node__lazy_reference(serialize_node):
    class LazyReferenceGenericNode(BaseNode):
        attr: str = LazyReference(lambda: ConstantValueReference("hello"))

    serialized_node = serialize_node(LazyReferenceGenericNode)

    assert not DeepDiff(
        {
            "id": "3d6bfe3b-263a-40a6-8a05-98288e9559a4",
            "label": "test_serialize_node__lazy_reference.<locals>.LazyReferenceGenericNode",
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
            "trigger": {"id": "14ec4d19-13e5-4db3-94fa-4e15274bffc7", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "2dba7224-a376-4780-8414-2b50601f9283", "name": "default", "type": "DEFAULT"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "7ae37eb4-18c8-49e1-b5ac-6369ce7ed5dd",
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


def test_serialize_node__workflow_input(serialize_node):
    class WorkflowInputGenericNode(BaseNode):
        attr: str = Inputs.input

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
                    "test_attributes_serialization",
                ],
            },
            "trigger": {"id": "debf37b9-720d-48dd-9699-69283966f927", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "20d91130-ca86-4420-b2e7-a962c0f1a509", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "6b2f781b-1a70-4abc-965a-a4edb8563f0e",
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


def test_serialize_node__workflow_input_as_nested_chat_history():
    # GIVEN workflow inputs as chat history
    class Inputs(BaseInputs):
        chat_history: List[ChatMessage]

    # AND a node referencing the workflow input
    class GenericNode(BaseNode):
        attr = {
            "hello": Inputs.chat_history,
        }

    # AND a workflow with the node
    class Workflow(BaseWorkflow[Inputs, BaseState]):
        graph = GenericNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay,
        workflow_class=Workflow,
    )
    with pytest.raises(Exception) as exc_info:
        workflow_display.serialize()

    # THEN we should raise a user facing error
    assert str(exc_info.value) == "Failed to serialize attribute 'attr': Nested references are not supported."


def test_serialize_node__node_output(serialize_node):
    class NodeWithOutput(BaseNode):
        class Outputs(BaseNode.Outputs):
            output = Inputs.input

    class NodeWithOutputDisplay(BaseNodeDisplay[NodeWithOutput]):
        pass

    class GenericNodeReferencingOutput(BaseNode):
        attr = NodeWithOutput.Outputs.output

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
            "id": "7210742f-8c3e-4379-9800-8b4b7f5dd7ed",
            "label": "test_serialize_node__node_output.<locals>.GenericNodeReferencingOutput",
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
            "trigger": {"id": "d4b08664-bb78-4fdd-83a2-877c4ca4175a", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "a345665a-decd-4f6b-af38-387bd41c2643", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "1318ab14-deb1-4254-9636-4bd783bdd9eb",
                    "name": "attr",
                    "value": {
                        "type": "NODE_OUTPUT",
                        "node_id": "48cf26cc-7b6d-49a7-a1a3-298f6d66772b",
                        "node_output_id": str(node_output_id),
                    },
                }
            ],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


def test_serialize_node__vellum_secret(serialize_node):
    class VellumSecretGenericNode(BaseNode):
        attr = VellumSecretReference(name="hello")

    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=VellumSecretGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    assert not DeepDiff(
        {
            "id": "0e75bd8f-882e-4ab7-8348-061319b574f7",
            "label": "test_serialize_node__vellum_secret.<locals>.VellumSecretGenericNode",
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
            "trigger": {"id": "70a3d4c0-83e3-428d-ac84-bf9e5644a84d", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "6d1c2139-64bd-4433-84d7-3fe08850134b", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "c2eb79e2-4cd3-4176-8da9-0d76327cbf0f",
                    "name": "attr",
                    "value": {"type": "VELLUM_SECRET", "vellum_secret_name": "hello"},
                }
            ],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


def test_serialize_node__node_execution(serialize_node):
    class NodeWithExecutions(BaseNode):
        pass

    class NodeWithExecutionsDisplay(BaseNodeDisplay[NodeWithExecutions]):
        pass

    class GenericNodeReferencingExecutions(BaseNode):
        attr: int = NodeWithExecutions.Execution.count

    workflow_input_id = uuid4()
    serialized_node = serialize_node(
        node_class=GenericNodeReferencingExecutions,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=workflow_input_id)},
        global_node_displays={NodeWithExecutions: NodeWithExecutionsDisplay()},
    )

    assert not DeepDiff(
        {
            "id": "f42dda6b-e856-49bd-b203-46c9dd66c08b",
            "label": "test_serialize_node__node_execution.<locals>.GenericNodeReferencingExecutions",
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
            "trigger": {"id": "0c06baa5-55b6-494a-a89d-9535dfa5f24b", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "59844b72-ac5e-43c5-b3a7-9c57ba73ec8c", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "8be1be85-ac70-4e61-b52a-cd416f5320b9",
                    "name": "attr",
                    "value": {
                        "type": "EXECUTION_COUNTER",
                        "node_id": "d68cc3c3-d5dc-4a51-bbfc-1fd4b41abad0",
                    },
                }
            ],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


def test_serialize_node__coalesce(serialize_node):
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
            "id": "bb99f326-7d2a-4b5e-95f3-6039114798da",
            "label": "test_serialize_node__coalesce.<locals>.CoalesceNodeFinal",
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
            "trigger": {"id": "b9894d9a-1887-416d-895d-a4129aac37b8", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "9d97a0c9-6a79-433a-bcdf-e07aa10c0f3c", "name": "default", "type": "DEFAULT"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "2e25b25b-4aac-425f-91f4-f0fa55453b8c",
                    "name": "attr",
                    "value": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
                            "type": "NODE_OUTPUT",
                            "node_id": "f6d1aa4d-c3fd-421d-9dc8-4209bddf7fd3",
                            "node_output_id": str(coalesce_node_a_output_id),
                        },
                        "operator": "coalesce",
                        "rhs": {
                            "type": "NODE_OUTPUT",
                            "node_id": "d1f673fb-80e1-4f9e-9d7d-afe64599ce39",
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
