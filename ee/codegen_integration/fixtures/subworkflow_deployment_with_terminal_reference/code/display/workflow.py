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
        entrypoint_node_id=UUID("entrypoint-node-id"),
        entrypoint_node_source_handle_id=UUID("entrypoint-source-handle"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=100, y=200), width=124, height=48),
        display_data=WorkflowDisplayData(viewport=WorkflowDisplayDataViewport(x=0, y=0, zoom=1)),
    )
    entrypoint_displays = {
        SubworkflowDeployment: EntrypointDisplay(
            id=UUID("entrypoint-node-id"), edge_display=EdgeDisplay(id=UUID("edge-1"))
        )
    }
    edge_displays = {(SubworkflowDeployment.Ports.default, FinalOutput): EdgeDisplay(id=UUID("edge-2"), z_index=None)}
    output_displays = {
        Workflow.Outputs.feedback: WorkflowOutputDisplay(id=UUID("workflow-output-feedback-id"), name="feedback"),
        Workflow.Outputs.feedback: WorkflowOutputDisplay(id=UUID("workflow-output-feedback-id"), name="feedback"),
    }
