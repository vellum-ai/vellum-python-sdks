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

from ..nodes.output import Output
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("49befc94-10a2-47ae-965b-a4a07c21305e"),
        entrypoint_node_source_handle_id=UUID("6b878e9a-95b2-404b-b5c2-abc8accc9320"),
        entrypoint_node_display=NodeDisplayData(
            position=NodeDisplayPosition(x=0, y=0),
            z_index=2,
            width=124,
            height=48,
            icon="vellum:icon:right-to-bracket",
            color="stone",
        ),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=49, y=345.9705304518664, zoom=0.962671905697446)
        ),
    )
    entrypoint_displays = {}
    output_displays = {
        Workflow.Outputs.output: WorkflowOutputDisplay(id=UUID("cb1ba284-84cf-4fb1-a57d-9fdb742646a0"), name="output")
    }
