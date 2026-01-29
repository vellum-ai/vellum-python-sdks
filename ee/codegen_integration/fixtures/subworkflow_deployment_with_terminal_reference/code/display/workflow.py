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
from ..nodes.subworkflow_deployment import SubworkflowDeployment
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("4c022a1c-99b3-4201-a67c-90bae1dfb11b"),
        entrypoint_node_source_handle_id=UUID("a3a606ee-4cc0-4bb7-950d-65bf8f125133"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=100, y=200), width=124, height=48),
        display_data=WorkflowDisplayData(viewport=WorkflowDisplayDataViewport(x=0, y=0, zoom=1)),
    )
    entrypoint_displays = {
        SubworkflowDeployment: EntrypointDisplay(
            id=UUID("4c022a1c-99b3-4201-a67c-90bae1dfb11b"),
            edge_display=EdgeDisplay(id=UUID("116b943a-748d-41f6-9cdf-0b65b8c73a76")),
        )
    }
    edge_displays = {
        (SubworkflowDeployment.Ports.default, FinalOutput): EdgeDisplay(
            id=UUID("e8f3a2b1-c4d5-4e6f-a7b8-9c0d1e2f3a4b"), z_index=None
        )
    }
    output_displays = {
        Workflow.Outputs.feedback: WorkflowOutputDisplay(
            id=UUID("d373db7e-fb81-45b1-a9e6-14e57ea570c8"), name="feedback"
        )
    }
