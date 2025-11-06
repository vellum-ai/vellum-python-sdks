import pytest
from uuid import UUID
from typing import Type

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.core.templating_node.node import TemplatingNode
from vellum_ee.workflows.display.nodes.vellum.templating_node import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def _no_display_class(Node: Type[TemplatingNode]):
    return None


def _display_class_with_node_input_ids_by_name(Node: Type[TemplatingNode]):
    class TemplatingNodeDisplay(BaseTemplatingNodeDisplay[Node]):  # type: ignore[valid-type]
        node_input_ids_by_name = {"foo": UUID("fba6a4d5-835a-4e99-afb7-f6a4aed15110")}

    return TemplatingNodeDisplay


def _display_class_with_node_input_ids_by_name_with_inputs_prefix(Node: Type[TemplatingNode]):
    class TemplatingNodeDisplay(BaseTemplatingNodeDisplay[Node]):  # type: ignore[valid-type]
        node_input_ids_by_name = {"inputs.foo": UUID("fba6a4d5-835a-4e99-afb7-f6a4aed15110")}

    return TemplatingNodeDisplay


@pytest.mark.parametrize(
    ["GetDisplayClass", "expected_input_id"],
    [
        (_no_display_class, "9567c1a5-fe6b-40b7-b268-72d48d3774d9"),
        (_display_class_with_node_input_ids_by_name, "fba6a4d5-835a-4e99-afb7-f6a4aed15110"),
        (_display_class_with_node_input_ids_by_name_with_inputs_prefix, "fba6a4d5-835a-4e99-afb7-f6a4aed15110"),
    ],
    ids=[
        "no_display_class",
        "display_class_with_node_input_ids_by_name",
        "display_class_with_node_input_ids_by_name_with_inputs_prefix",
    ],
)
def test_serialize_node__templating_node_inputs(GetDisplayClass, expected_input_id):
    # GIVEN a templating node with inputs
    class MyTemplatingNode(TemplatingNode):
        inputs = {"foo": "bar"}

    # AND a workflow with the templating node
    class Workflow(BaseWorkflow):
        graph = MyTemplatingNode

    # AND a display class
    GetDisplayClass(MyTemplatingNode)

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the inputs
    my_templating_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["type"] == "TEMPLATING"
    )

    assert my_templating_node["inputs"] == [
        {
            "id": "b16c661b-b662-4f3f-8a99-9df615e396b9",
            "key": "template",
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
    ]
