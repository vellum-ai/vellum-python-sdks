from typing import Any, Dict, cast

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.templating_node.node import TemplatingNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_try_node_display__serialize_with_error_output() -> None:
    # GIVEN a Base Node wrapped with a TryNode
    @TryNode.wrap()
    class MyNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            hello = "world"

    # AND a displayable node referencing
    class OtherNode(TemplatingNode):
        template = "{{ hello }} {{ error }}"
        inputs = {
            "hello": MyNode.Outputs.hello,
            "error": MyNode.Outputs.error,
        }

    # AND a workflow referencing the two nodes
    class MyWorkflow(BaseWorkflow):
        graph = MyNode >> OtherNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    serialized_workflow = cast(Dict[str, Any], workflow_display.serialize())

    # THEN the correct inputs should be serialized on the node
    serialized_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["id"] == str(OtherNode.__id__)
    )
    hello_input_value = next(input["value"] for input in serialized_node["inputs"] if input["key"] == "hello")
    error_input_value = next(input["value"] for input in serialized_node["inputs"] if input["key"] == "error")
    assert hello_input_value == {
        "combinator": "OR",
        "rules": [
            {
                "data": {
                    "node_id": str(MyNode.__wrapped_node__.__id__),
                    "output_id": "75bb6e13-0cf0-4651-9141-658be1d5acaa",
                },
                "type": "NODE_OUTPUT",
            }
        ],
    }
    assert error_input_value == {
        "combinator": "OR",
        "rules": [
            {
                "data": {
                    "node_id": str(MyNode.__wrapped_node__.__id__),
                    "output_id": "16b4d0ee-d309-4622-b812-3bd8f8c8a73c",
                },
                "type": "NODE_OUTPUT",
            }
        ],
    }
