from uuid import UUID

from vellum_ee.workflows.display.base import EdgeDisplay, WorkflowOutputDisplay
from vellum_ee.workflows.display.vellum import (
    EntrypointVellumDisplayOverrides,
    NodeDisplayData,
    NodeDisplayPosition,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowInputsVellumDisplayOverrides,
    WorkflowMetaVellumDisplayOverrides,
)
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay

from ..inputs import Inputs
from ..nodes.final_output import FinalOutput
from ..nodes.templating_node import TemplatingNode
from ..workflow import Workflow


class WorkflowDisplay(VellumWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaVellumDisplayOverrides(
        entrypoint_node_id=UUID("39a5155a-d137-4a56-be36-d525802df463"),
        entrypoint_node_source_handle_id=UUID("beddfefc-dc34-483d-b313-f6a2a2e0737e"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-803.590909090909, y=155.55369283943529, zoom=0.5494263018534863)
        ),
    )
    inputs_display = {
        Inputs.text: WorkflowInputsVellumDisplayOverrides(
            id=UUID("93b9d3fb-251c-4a53-a1d5-4bd8e61947c5"), name="text", required=True
        )
    }
    entrypoint_displays = {
        TemplatingNode: EntrypointVellumDisplayOverrides(
            id=UUID("39a5155a-d137-4a56-be36-d525802df463"),
            edge_display=EdgeDisplay(id=UUID("e659e56b-89a7-49d0-b792-b27006242fe1")),
        )
    }
    edge_displays = {
        (TemplatingNode.Ports.default, FinalOutput): EdgeDisplay(id=UUID("dd79b52e-5a4d-4e62-9f83-9dd2468ca891"))
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("4dc6e13e-92ba-436e-aa35-87e258f2f585"), name="final-output"
        )
    }
