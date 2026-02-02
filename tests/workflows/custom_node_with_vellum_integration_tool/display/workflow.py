from uuid import UUID

from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EntrypointDisplay,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowMetaDisplay,
)
from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay

from ..nodes.custom_node_with_integration_tool import CustomNodeWithIntegrationTool
from ..workflow import CustomNodeWithVellumIntegrationToolWorkflow


class CustomNodeWithVellumIntegrationToolWorkflowDisplay(
    BaseWorkflowDisplay[CustomNodeWithVellumIntegrationToolWorkflow]
):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("dd30ba80-ab6d-4daf-b9d0-3a339b4428dd"),
        entrypoint_node_source_handle_id=UUID("dd1cef7a-ebb1-454b-a625-6caf1ae4a8e1"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=0, y=0)),
        display_data=WorkflowDisplayData(viewport=WorkflowDisplayDataViewport(x=0, y=0, zoom=1)),
    )
    entrypoint_displays = {
        CustomNodeWithIntegrationTool: EntrypointDisplay(
            id=UUID("dd30ba80-ab6d-4daf-b9d0-3a339b4428dd"),
            edge_display=EdgeDisplay(id=UUID("7be3200f-5ef8-456a-be60-fb29a7374875")),
        )
    }
    output_displays = {}
