import pytest
from uuid import uuid4

from deepdiff import DeepDiff

from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.nodes.vellum.base_node import BaseNodeDisplay
from vellum_ee.workflows.display.tests.workflow_serialization.generic_nodes.basic import BasicGenericNode
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.vellum import NodeDisplayData, WorkflowMetaVellumDisplay
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


@pytest.fixture()
def serialize_node():
    def _serialize_node(node_class) -> dict:
        node_display_class = get_node_display_class(BaseNodeDisplay, node_class)
        node_display = node_display_class()

        context: WorkflowDisplayContext = WorkflowDisplayContext(
            workflow_display_class=VellumWorkflowDisplay,
            workflow_display=WorkflowMetaVellumDisplay(
                entrypoint_node_id=uuid4(),
                entrypoint_node_source_handle_id=uuid4(),
                entrypoint_node_display=NodeDisplayData(),
            ),
            node_displays={node_class: node_display},
        )
        return node_display.serialize(context)

    return _serialize_node


def test_serialize_node__basic(serialize_node):
    serialized_node = serialize_node(BasicGenericNode)
    assert not DeepDiff(
        {
            "id": "c2ed23f7-f6cb-4a56-a91c-2e5f9d8fda7f",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "definition": {
                "name": "BasicGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "basic",
                ],
                "bases": [{"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]}],
            },
            "ports": [],
            "trigger": {"id": "9d3a1b3d-4a38-4f2e-bbf1-dd8be152bce8", "merge_behavior": "AWAIT_ANY"},
        },
        serialized_node,
        ignore_order=True,
    )
