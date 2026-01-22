from uuid import UUID

from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EntrypointDisplay,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowMetaDisplay,
    WorkflowOutputDisplay,
)
from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay

from ....nodes.node.nodes.my_subworkflow import MySubworkflowNode
from ....nodes.node.workflow import MyNodeWorkflow


class MyNodeWorkflowDisplay(BaseWorkflowDisplay[MyNodeWorkflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("0fc5a026-f775-43f6-9761-dd68f3b3dbb4"),
        entrypoint_node_source_handle_id=UUID("eb9225cc-863b-4ef4-adb4-93f058ebb573"),
        display_data=WorkflowDisplayData(viewport=WorkflowDisplayDataViewport(x=0, y=0, zoom=1)),
    )
    entrypoint_displays = {
        MySubworkflowNode: EntrypointDisplay(
            id=UUID("0fc5a026-f775-43f6-9761-dd68f3b3dbb4"),
            edge_display=EdgeDisplay(id=UUID("1a526045-0550-488b-a6c4-29bc86050bcd")),
        )
    }
    output_displays = {
        MyNodeWorkflow.Outputs.result: WorkflowOutputDisplay(
            id=UUID("4b59eb8b-8f00-4e8f-91d6-423eff3d4663"), name="result"
        )
    }
