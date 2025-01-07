from uuid import uuid4

from ee.vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from ee.vellum_ee.workflows.display.nodes.vellum.base_node import BaseNodeDisplay
from ee.vellum_ee.workflows.display.tests.workflow_serialization.generic_nodes.nodes import BasicGenericNode
from ee.vellum_ee.workflows.display.types import WorkflowDisplayContext
from ee.vellum_ee.workflows.display.vellum import NodeDisplayData, WorkflowMetaVellumDisplay
from ee.vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


def test_serialize_node__basic():
    node_display_class = get_node_display_class(BaseNodeDisplay, BasicGenericNode)
    node_display = node_display_class()

    context = WorkflowDisplayContext(
        workflow_display_class=VellumWorkflowDisplay,
        workflow_display=WorkflowMetaVellumDisplay(
            entrypoint_node_id=uuid4(),
            entrypoint_node_source_handle_id=uuid4(),
            entrypoint_node_display=NodeDisplayData(),
        ),
        node_displays={BasicGenericNode: node_display},
    )
    node_display.serialize(context)
