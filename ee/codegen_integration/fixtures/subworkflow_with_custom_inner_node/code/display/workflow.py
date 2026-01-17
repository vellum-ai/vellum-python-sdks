from uuid import UUID

from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EntrypointDisplay,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowMetaDisplay,
    WorkflowOutputDisplay,
)
from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay

from ..nodes.node import MySubworkflowNode
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("63884a7b-c01c-4cbc-b8d4-abe0a8796f6b"),
        entrypoint_node_source_handle_id=UUID("eba8fd73-57ab-4d7b-8f75-b54dbe5fc8ba"),
        entrypoint_node_display=NodeDisplayData(
            position=NodeDisplayPosition(x=-30, y=0),
            z_index=1,
            width=306,
            height=88,
            icon="vellum:icon:play",
            color="default",
        ),
        display_data=WorkflowDisplayData(viewport=WorkflowDisplayDataViewport(x=0, y=0, zoom=1)),
    )
    entrypoint_displays = {
        MySubworkflowNode: EntrypointDisplay(
            id=UUID("63884a7b-c01c-4cbc-b8d4-abe0a8796f6b"),
            edge_display=EdgeDisplay(id=UUID("227a29f5-cfaf-4dc4-b9d9-7a5bd5c508ad")),
        )
    }
    output_displays = {
        Workflow.Outputs.result: WorkflowOutputDisplay(id=UUID("6a2f0fad-8670-4cee-b2b2-c94ad3b4807f"), name="result")
    }
