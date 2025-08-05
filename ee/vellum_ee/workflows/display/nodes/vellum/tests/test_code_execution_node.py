import pytest
from uuid import UUID
from typing import Type

from vellum.client.core.api_error import ApiError
from vellum.workflows.nodes.displayable.code_execution_node.node import CodeExecutionNode
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.nodes.vellum.code_execution_node import BaseCodeExecutionNodeDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def _no_display_class(Node: Type[CodeExecutionNode]):
    return None


def _display_class_with_node_input_ids_by_name(Node: Type[CodeExecutionNode]):
    class CodeExecutionNodeDisplay(BaseCodeExecutionNodeDisplay[Node]):  # type: ignore[valid-type]
        node_input_ids_by_name = {"foo": UUID("fba6a4d5-835a-4e99-afb7-f6a4aed15110")}

    return CodeExecutionNodeDisplay


def _display_class_with_node_input_ids_by_name_with_inputs_prefix(Node: Type[CodeExecutionNode]):
    class CodeExecutionNodeDisplay(BaseCodeExecutionNodeDisplay[Node]):  # type: ignore[valid-type]
        node_input_ids_by_name = {"code_inputs.foo": UUID("fba6a4d5-835a-4e99-afb7-f6a4aed15110")}

    return CodeExecutionNodeDisplay


@pytest.mark.parametrize(
    ["GetDisplayClass", "expected_input_id"],
    [
        (_no_display_class, "a5dbe403-0b00-4df6-b8f7-ed5f7794b003"),
        (_display_class_with_node_input_ids_by_name, "fba6a4d5-835a-4e99-afb7-f6a4aed15110"),
        (_display_class_with_node_input_ids_by_name_with_inputs_prefix, "fba6a4d5-835a-4e99-afb7-f6a4aed15110"),
    ],
    ids=[
        "no_display_class",
        "display_class_with_node_input_ids_by_name",
        "display_class_with_node_input_ids_by_name_with_inputs_prefix",
    ],
)
def test_serialize_node__code_node_inputs(GetDisplayClass, expected_input_id):
    # GIVEN a code node with inputs
    class MyCodeExecutionNode(CodeExecutionNode):
        code_inputs = {"foo": "bar"}

    # AND a workflow with the code node
    class Workflow(BaseWorkflow):
        graph = MyCodeExecutionNode

    # AND a display class
    GetDisplayClass(MyCodeExecutionNode)

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the inputs
    my_code_execution_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["type"] == "CODE_EXECUTION"
    )

    assert my_code_execution_node["inputs"] == [
        {
            "id": expected_input_id,
            "key": "foo",
            "value": {
                "combinator": "OR",
                "rules": [
                    {
                        "type": "CONSTANT_VALUE",
                        "data": {
                            "type": "STRING",
                            "value": "bar",
                        },
                    }
                ],
            },
        },
        {
            "id": "9774d864-c76d-4a1a-8181-b632ed3ab87c",
            "key": "code",
            "value": {
                "combinator": "OR",
                "rules": [
                    {
                        "type": "CONSTANT_VALUE",
                        "data": {
                            "type": "STRING",
                            "value": "",
                        },
                    }
                ],
            },
        },
        {
            "id": "34742235-5699-45cd-9d34-bce3745e743d",
            "key": "runtime",
            "value": {
                "combinator": "OR",
                "rules": [
                    {
                        "type": "CONSTANT_VALUE",
                        "data": {
                            "type": "STRING",
                            "value": "PYTHON_3_11_6",
                        },
                    }
                ],
            },
        },
    ]


def test_serialize_node__with_unresolved_secret_references(vellum_client):
    # GIVEN a node has access to a secret reference
    class MyNode(CodeExecutionNode):
        code_inputs = {"api_key": VellumSecretReference("MY_API_KEY")}

    # AND the secret is not found
    vellum_client.workspace_secrets.retrieve.side_effect = ApiError(
        status_code=404,
        body="Secret not found",
    )

    # AND a workflow with the code node
    class Workflow(BaseWorkflow):
        graph = MyNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=Workflow)
    data: dict = workflow_display.serialize()

    # THEN the condition should be serialized correctly
    node = next(node for node in data["workflow_raw_data"]["nodes"] if node["type"] == "CODE_EXECUTION")
    assert node["inputs"][0]["value"] == {
        "combinator": "OR",
        "rules": [
            {
                "type": "WORKSPACE_SECRET",
                "data": {
                    "type": "STRING",
                    "workspace_secret_id": None,
                },
            }
        ],
    }

    # AND we should have a warning of the invalid reference
    # TODO: Come up with a proposal for how nodes should propagate warnings
    # warnings = list(workflow_display.errors)
    # assert len(warnings) == 1
    # assert "Failed to resolve secret reference 'MY_API_KEY'" in str(warnings[0])
