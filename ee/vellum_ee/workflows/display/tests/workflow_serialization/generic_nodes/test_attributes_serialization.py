import pytest
from dataclasses import dataclass
from uuid import uuid4
from typing import List

from deepdiff import DeepDiff
from pydantic import BaseModel

from vellum.client.types.chat_message import ChatMessage
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.references.environment_variable import EnvironmentVariableReference
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.base import WorkflowInputsDisplay
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class Inputs(BaseInputs):
    input: str


def test_serialize_node__constant_value(serialize_node):
    class ConstantValueGenericNode(BaseNode):
        attr: str = "hello"

    serialized_node = serialize_node(ConstantValueGenericNode)

    assert not DeepDiff(
        {
            "id": "115acb09-8bb4-4088-a76a-99a145802c00",
            "label": "Constant Value Generic Node",
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
            "trigger": {"id": "3522f3b2-5e4e-4296-a7b9-09849c57ec57", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "72cf5f4b-9c3e-4e0c-989e-f44c04652280", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "889e90b4-a139-4f75-85a3-21d3974dccef",
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


@pytest.mark.parametrize(
    "boolean_value, expected_value",
    [
        (True, True),
        (False, False),
    ],
)
def test_serialize_node__constant_boolean_value(serialize_node, boolean_value, expected_value):
    class BooleanValueGenericNode(BaseNode):
        attr: bool = boolean_value

    serialized_node = serialize_node(BooleanValueGenericNode)

    assert serialized_node["attributes"][0]["value"] == {
        "type": "CONSTANT_VALUE",
        "value": {
            "type": "JSON",
            "value": expected_value,
        },
    }


def test_serialize_node__constant_value_reference(serialize_node):
    class ConstantValueReferenceGenericNode(BaseNode):
        attr: str = ConstantValueReference("hello")

    serialized_node = serialize_node(ConstantValueReferenceGenericNode)

    assert not DeepDiff(
        {
            "id": "e99eebee-2a3d-488f-9365-7210de6daef9",
            "label": "Constant Value Reference Generic Node",
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
            "trigger": {"id": "e1a16f8a-5ab4-463f-a888-b9d2699af96d", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "6a1632c7-232f-4546-b2fe-94381f7a670e", "name": "default", "type": "DEFAULT"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "35885b7e-bca5-4053-96c1-a2bcf5530348",
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
    attributes = serialized_node["attributes"]

    assert attributes == [
        {
            "id": "7d98966d-8ef0-4fc4-ac90-2f1d46da0ba4",
            "name": "attr",
            "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "hello"}},
        }
    ]


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
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the attribute reference
    lazy_reference_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(LazyReferenceGenericNode.__id__)
    )

    assert lazy_reference_node["attributes"] == [
        {
            "id": "c8da84b7-fd1b-4629-a80b-a31eabada2a9",
            "name": "attr",
            "value": {
                "type": "NODE_OUTPUT",
                "node_id": str(OtherNode.__id__),
                "node_output_id": "3c28ab49-1c7c-42cc-8175-be17bf05b5e7",
            },
        }
    ]


def test_serialize_node__lazy_reference_workflow_output():
    """Test that LazyReference to workflow output serializes as WORKFLOW_OUTPUT type."""

    # GIVEN a node with a LazyReference to a workflow output
    class NodeWithWorkflowOutputReference(BaseNode):
        workflow_output_ref = LazyReference(lambda: TestWorkflow.Outputs.final_result)

    class TestNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str = "test result"

    # AND a workflow that defines an output
    class TestWorkflow(BaseWorkflow):
        graph = NodeWithWorkflowOutputReference >> TestNode

        class Outputs(BaseWorkflow.Outputs):
            final_result = TestNode.Outputs.result

    # WHEN the node is serialized in the context of the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the workflow output reference
    node_with_lazy_reference = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(NodeWithWorkflowOutputReference.__id__)
    )

    # AND the workflow output reference should serialize as WORKFLOW_OUTPUT type
    assert len(node_with_lazy_reference["attributes"]) == 1
    attr = node_with_lazy_reference["attributes"][0]
    assert attr["name"] == "workflow_output_ref"
    assert attr["value"]["type"] == "WORKFLOW_OUTPUT"

    # AND the output_variable_id should match the workflow output
    workflow_output = next(
        output for output in serialized_workflow["output_variables"] if output["key"] == "final_result"
    )
    assert attr["value"]["output_variable_id"] == workflow_output["id"]


def test_serialize_node__lazy_reference_workflow_output_with_string():
    """Test that string-based LazyReference to workflow output serializes as WORKFLOW_OUTPUT type."""

    # GIVEN a node with a string-based LazyReference to a workflow output
    class NodeWithWorkflowOutputReference(BaseNode):
        workflow_output_ref = LazyReference[str]("StringWorkflow.Outputs.final_result")

    class TestNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str = "test result"

    # AND a workflow that defines an output
    class StringWorkflow(BaseWorkflow):
        graph = NodeWithWorkflowOutputReference >> TestNode

        class Outputs(BaseWorkflow.Outputs):
            final_result = TestNode.Outputs.result

    # WHEN the node is serialized in the context of the workflow
    workflow_display = get_workflow_display(workflow_class=StringWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the workflow output reference
    node_with_lazy_reference = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(NodeWithWorkflowOutputReference.__id__)
    )

    # AND the workflow output reference should serialize as WORKFLOW_OUTPUT type
    assert len(node_with_lazy_reference["attributes"]) == 1
    attr = node_with_lazy_reference["attributes"][0]
    assert attr["name"] == "workflow_output_ref"
    assert attr["value"]["type"] == "WORKFLOW_OUTPUT"

    # AND the output_variable_id should match the workflow output
    workflow_output = next(
        output for output in serialized_workflow["output_variables"] if output["key"] == "final_result"
    )
    assert attr["value"]["output_variable_id"] == workflow_output["id"]


def test_serialize_node__lazy_reference_with_string__class_not_found():
    """Test that InvalidOutputReferenceError is added to display context when the referenced class is not found."""

    # GIVEN a node with a string-based LazyReference to a non-existent class
    class NodeWithInvalidReference(BaseNode):
        invalid_ref = LazyReference[str]("NonExistentClass.Outputs.result")

    # AND a workflow that contains the node
    class TestWorkflow(BaseWorkflow):
        graph = NodeWithInvalidReference

    # WHEN we try to serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    workflow_display.serialize()

    # THEN the error should be added to the display context
    errors = list(workflow_display.display_context.errors)
    assert len(errors) == 1

    # AND the error message should mention the class that could not be found
    error_message = str(errors[0])
    assert "NonExistentClass" in error_message
    assert "Could not find node or workflow class" in error_message


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
                    "test_attributes_serialization",
                ],
            },
            "trigger": {"id": "f8a79f35-b083-47d1-80ee-5efc2baa54e5", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "78878dd7-87fc-4f93-b340-0e1155260f23", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "23fddc82-c5a9-4aee-b736-2484518d6779",
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
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the attribute reference
    generic_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["id"] == str(GenericNode.__id__)
    )

    assert not DeepDiff(
        {
            "id": "6cf118f2-f550-493b-b49e-c24d4001baea",
            "label": "Generic Node",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "GenericNode",
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
            "trigger": {"id": "33ad6542-c6bc-4030-a110-167e37cceb7b", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "1f963bfe-d826-452c-8f1f-9f23e350b299", "name": "default", "type": "DEFAULT"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "07ca2e5d-0215-45c7-bcf5-88b2f5fe2dd3",
                    "name": "attr",
                    "value": {
                        "type": "DICTIONARY_REFERENCE",
                        "entries": [
                            {
                                "id": "03260b95-1648-4a60-9c4a-51402b3d9a3a",
                                "key": "hello",
                                "value": {
                                    "type": "WORKFLOW_INPUT",
                                    "input_variable_id": "f727c3f9-f27f-4ac9-abd7-12bf612a094e",
                                },
                            }
                        ],
                    },
                }
            ],
            "outputs": [],
        },
        generic_node,
        ignore_order=True,
    )


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
            NodeWithOutput.Outputs.output: NodeOutputDisplay(id=node_output_id, name="output")
        },
    )

    assert not DeepDiff(
        {
            "id": "b79e1e71-a81d-4cb6-a4cb-efa8fc350e9f",
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
                    "test_attributes_serialization",
                ],
            },
            "trigger": {"id": "4dc05332-fc5d-420e-ae39-5186329bc6a7", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "9fd4e17b-e270-40e9-8e34-6b4203839648", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "4455b900-fae8-45d6-8791-af2b4c324519",
                    "name": "attr",
                    "value": {
                        "type": "NODE_OUTPUT",
                        "node_id": "e253523d-da42-405f-b44f-24999a1ea2b0",
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
            "id": "7400819d-68dc-4469-a390-2ca908e827f4",
            "label": "Vellum Secret Generic Node",
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
            "trigger": {"id": "299e9fca-dab9-42df-ac49-ef4e69fe8abd", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "65a83e3e-e8b4-4744-a200-109ff0148ae8", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "2cc1113c-69db-42f1-a378-d09414a3cb2c",
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
            "id": "8f96a3df-ea29-48a5-a5f3-5ef95296d25f",
            "label": "Generic Node Referencing Executions",
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
            "trigger": {"id": "ecd645fb-8079-4217-ac35-720993845899", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "faed7c7b-3aed-4662-8b36-5c6ce92c6754", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "235d400b-e46e-46fd-9a75-8d1220bee29d",
                    "name": "attr",
                    "value": {
                        "type": "EXECUTION_COUNTER",
                        "node_id": "d1edee11-6fa1-4ccf-a62c-9f7ca3d446da",
                    },
                }
            ],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


def test_serialize_node__environment_variable(serialize_node):
    class EnvironmentVariableGenericNode(BaseNode):
        attr = EnvironmentVariableReference(name="API_KEY")

    serialized_node = serialize_node(EnvironmentVariableGenericNode)

    expected_value = {
        "type": "ENVIRONMENT_VARIABLE",
        "environment_variable": "API_KEY",
    }

    actual_value = serialized_node["attributes"][0]["value"]
    assert actual_value == expected_value


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
            CoalesceNodeA.Outputs.output: NodeOutputDisplay(id=coalesce_node_a_output_id, name="output"),
            CoalesceNodeB.Outputs.output: NodeOutputDisplay(id=coalesce_node_b_output_id, name="output"),
        },
    )

    assert not DeepDiff(
        {
            "id": "fc3216ee-4ab4-4856-b660-d9158e72ed5f",
            "label": "Coalesce Node Final",
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
            "trigger": {"id": "80b9055b-e1da-454c-babc-b1605c5cfab3", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "4ceb95a9-c257-4492-828f-ebcdc685d8b0", "name": "default", "type": "DEFAULT"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "f5fba9a8-0d90-4a99-a5b0-9f95a61e61d1",
                    "name": "attr",
                    "value": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
                            "type": "NODE_OUTPUT",
                            "node_id": "bacedc11-f833-4bce-80e6-4becbf002fd0",
                            "node_output_id": str(coalesce_node_a_output_id),
                        },
                        "operator": "coalesce",
                        "rhs": {
                            "type": "NODE_OUTPUT",
                            "node_id": "1637e989-eb51-4edd-a4d9-831cb5e58368",
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


def test_serialize_node__dataclass_with_node_output_reference(serialize_node):
    @dataclass
    class MyDataClass:
        name: str
        node_ref: str

    class NodeWithOutput(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    class NodeWithOutputDisplay(BaseNodeDisplay[NodeWithOutput]):
        pass

    class GenericNodeWithDataclass(BaseNode):
        attr = MyDataClass(name="test", node_ref=NodeWithOutput.Outputs.result)

    node_output_id = uuid4()
    serialized_node = serialize_node(
        node_class=GenericNodeWithDataclass,
        global_node_displays={NodeWithOutput: NodeWithOutputDisplay()},
        global_node_output_displays={
            NodeWithOutput.Outputs.result: NodeOutputDisplay(id=node_output_id, name="result")
        },
    )

    attr_value = serialized_node["attributes"][0]["value"]
    assert attr_value["type"] == "DICTIONARY_REFERENCE"

    assert any(
        entry["key"] == "node_ref" and entry["value"]["type"] == "NODE_OUTPUT" for entry in attr_value["entries"]
    )


def test_serialize_node__pydantic_with_node_output_reference(serialize_node):
    class MyPydanticModel(BaseModel):
        name: str
        node_ref: str

    class NodeWithOutput(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    class NodeWithOutputDisplay(BaseNodeDisplay[NodeWithOutput]):
        pass

    class GenericNodeWithPydantic(BaseNode):
        attr = MyPydanticModel(name="test", node_ref=NodeWithOutput.Outputs.result)

    node_output_id = uuid4()
    serialized_node = serialize_node(
        node_class=GenericNodeWithPydantic,
        global_node_displays={NodeWithOutput: NodeWithOutputDisplay()},
        global_node_output_displays={
            NodeWithOutput.Outputs.result: NodeOutputDisplay(id=node_output_id, name="result")
        },
    )

    attr_value = serialized_node["attributes"][0]["value"]
    assert attr_value["type"] == "DICTIONARY_REFERENCE"

    assert any(
        entry["key"] == "node_ref" and entry["value"]["type"] == "NODE_OUTPUT" for entry in attr_value["entries"]
    )


def test_serialize_node__comment_expanded_true_when_content_exists(serialize_node):
    """
    Tests that node comment serialization sets expanded=True when comment has content.
    """

    class NodeWithComment(BaseNode):
        """This is a test comment for the node."""

        pass

    serialized_node = serialize_node(NodeWithComment)

    # WHEN the node is serialized
    display_data = serialized_node["display_data"]

    # THEN the comment should have expanded=True
    assert "comment" in display_data
    assert display_data["comment"]["value"] == "This is a test comment for the node."
    assert display_data["comment"]["expanded"] is True


def test_serialize_node__comment_expanded_preserved_when_explicitly_set(serialize_node):
    """
    Tests that explicitly set expanded value is preserved during serialization.
    """
    from vellum_ee.workflows.display.editor.types import NodeDisplayComment, NodeDisplayData
    from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay

    class NodeWithExplicitComment(BaseNode):
        """This is a test comment."""

        pass

    class NodeWithExplicitCommentDisplay(BaseNodeDisplay[NodeWithExplicitComment]):
        display_data = NodeDisplayData(comment=NodeDisplayComment(value="Custom comment", expanded=False))

    serialized_node = serialize_node(
        NodeWithExplicitComment,
        global_node_displays={NodeWithExplicitComment: NodeWithExplicitCommentDisplay()},
    )

    # WHEN the node is serialized
    display_data = serialized_node["display_data"]

    # THEN the comment should preserve expanded=False
    assert "comment" in display_data
    assert display_data["comment"]["value"] == "This is a test comment."
    assert display_data["comment"]["expanded"] is False


def test_serialize_node__attribute_with_type_annotation_no_default(serialize_node):
    """
    Tests that attributes with type annotations but no default values serialize as None.
    """

    # GIVEN a node with typed attributes but no default values
    class NodeWithTypedAttributesNoDefault(BaseNode):
        attr: str

    # WHEN the node is serialized
    serialized_node = serialize_node(NodeWithTypedAttributesNoDefault)

    # THEN the attribute should serialize as None
    assert serialized_node["attributes"][0]["value"] is None
