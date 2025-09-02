from uuid import UUID

from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EntrypointDisplay,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowInputsDisplay,
    WorkflowMetaDisplay,
    WorkflowOutputDisplay,
)
from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay

from ..inputs import Inputs
from ..nodes.final_output import FinalOutput
from ..nodes.templating_node import TemplatingNode
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("39a5155a-d137-4a56-be36-d525802df463"),
        entrypoint_node_source_handle_id=UUID("beddfefc-dc34-483d-b313-f6a2a2e0737e"),
        entrypoint_node_display=NodeDisplayData(
            position=NodeDisplayPosition(x=1545, y=330), z_index=None, width=124, height=48
        ),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-803.590909090909, y=155.55369283943529, zoom=0.5494263018534863)
        ),
    )
    inputs_display = {Inputs.text: WorkflowInputsDisplay(id=UUID("93b9d3fb-251c-4a53-a1d5-4bd8e61947c5"), name="text")}
    entrypoint_displays = {
        TemplatingNode: EntrypointDisplay(
            id=UUID("39a5155a-d137-4a56-be36-d525802df463"),
            edge_display=EdgeDisplay(id=UUID("e659e56b-89a7-49d0-b792-b27006242fe1")),
        )
    }
    edge_displays = {
        (TemplatingNode.Ports.default, FinalOutput): EdgeDisplay(
            id=UUID("dd79b52e-5a4d-4e62-9f83-9dd2468ca891"), z_index=None
        )
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("4dc6e13e-92ba-436e-aa35-87e258f2f585"), name="final-output"
        )
    }
