from typing import Any, Dict, cast

from vellum.client.types.vellum_error import VellumError
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.core.error_node.node import ErrorNode
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


def test_error_node_display__serialize_with_vellum_error() -> None:
    # GIVEN an Error Node with a VellumError
    class MyNode(ErrorNode):
        error = VellumError(
            message="A bad thing happened",
            code="USER_DEFINED_ERROR",
        )

    # AND a workflow referencing the two node
    class MyWorkflow(BaseWorkflow):
        graph = MyNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(base_display_class=VellumWorkflowDisplay, workflow_class=MyWorkflow)
    serialized_workflow = cast(Dict[str, Any], workflow_display.serialize())

    # THEN the correct inputs should be serialized on the node
    serialized_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["id"] == str(MyNode.__id__)
    )
    assert serialized_node["inputs"][0]["value"] == {
        "combinator": "OR",
        "rules": [
            {
                "data": {
                    "type": "ERROR",
                    "value": {
                        "message": "A bad thing happened",
                        "code": "USER_DEFINED_ERROR",
                    },
                },
                "type": "CONSTANT_VALUE",
            }
        ],
    }
