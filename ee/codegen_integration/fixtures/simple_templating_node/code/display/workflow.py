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

from ..nodes.final_output import FinalOutput
from ..nodes.templating_node import TemplatingNode
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("6b52893a-e649-434d-aedd-e8ad73d78dce"),
        entrypoint_node_source_handle_id=UUID("b4f25dad-17c6-464d-b347-9945065f17e4"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-992.7774269608426, y=-82.38774859214823, zoom=0.6534253694599966)
        ),
    )
    entrypoint_displays = {
        TemplatingNode: EntrypointDisplay(
            id=UUID("6b52893a-e649-434d-aedd-e8ad73d78dce"),
            edge_display=EdgeDisplay(id=UUID("662141c0-23b1-4513-9b8a-e382e56c4021")),
        )
    }
    edge_displays = {
        (TemplatingNode.Ports.default, FinalOutput): EdgeDisplay(
            id=UUID("6deb7d8b-b4cc-488f-aa30-e3e5f0957882"), z_index=None
        )
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("b0961a8d-f702-4922-b410-2aecf7d34b68"), name="final-output"
        )
    }
