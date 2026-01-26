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

from ..nodes.workflow import ContextAwareToolNode
from ..workflow import ToolCallingNodeWithWorkflowContextWorkflow


class ToolCallingNodeWithWorkflowContextWorkflowDisplay(
    BaseWorkflowDisplay[ToolCallingNodeWithWorkflowContextWorkflow]
):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("9c2fa689-ec2c-4ac1-a2a5-8ae93d1c5002"),
        entrypoint_node_source_handle_id=UUID("0e309c50-1074-414c-8be1-04028ddb2256"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=0, y=0)),
        display_data=WorkflowDisplayData(viewport=WorkflowDisplayDataViewport(x=0, y=0, zoom=1)),
    )
    entrypoint_displays = {
        ContextAwareToolNode: EntrypointDisplay(
            id=UUID("9c2fa689-ec2c-4ac1-a2a5-8ae93d1c5002"),
            edge_display=EdgeDisplay(id=UUID("0bb316e6-1ff0-4ee1-80de-07c39c33d1a5")),
        )
    }
    output_displays = {
        ToolCallingNodeWithWorkflowContextWorkflow.Outputs.text: WorkflowOutputDisplay(
            id=UUID("1fc17933-7950-4a8a-a632-6b83f00e0796"), name="text"
        ),
        ToolCallingNodeWithWorkflowContextWorkflow.Outputs.chat_history: WorkflowOutputDisplay(
            id=UUID("cd8fef68-a23e-4df6-87f1-996b4e5e32cf"), name="chat_history"
        ),
    }
