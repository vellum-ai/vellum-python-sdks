import pytest
from uuid import UUID
from typing import Type

from vellum.workflows.nodes.displayable.code_execution_node.node import CodeExecutionNode
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.nodes.vellum.code_execution_node import BaseCodeExecutionNodeDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


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
        (_no_display_class, "e3cdb222-324e-4ad1-abb2-bdd7881b3a0e"),
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
    workflow_display = get_workflow_display(base_display_class=VellumWorkflowDisplay, workflow_class=Workflow)
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
