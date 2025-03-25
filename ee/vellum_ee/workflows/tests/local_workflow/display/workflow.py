from uuid import UUID

from vellum_ee.workflows.display.base import EdgeDisplay
from vellum_ee.workflows.display.vellum import (
    EntrypointVellumDisplayOverrides,
    NodeDisplayData,
    NodeDisplayPosition,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowInputsVellumDisplayOverrides,
    WorkflowMetaVellumDisplayOverrides,
    WorkflowOutputVellumDisplayOverrides,
)
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay

from ..inputs import Inputs
from ..nodes.final_output import FinalOutput
from ..nodes.templating_node import TemplatingNode
from ..workflow import Workflow


class WorkflowDisplay(VellumWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaVellumDisplayOverrides(
        entrypoint_node_id=UUID("0bf86989-13f2-438c-ab9c-d172e5771d31"),
        entrypoint_node_source_handle_id=UUID("23448f09-81ad-4378-abbd-1cccff350627"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-1137.2395104895104, y=110.60314685314688, zoom=0.7779720279720279)
        ),
    )
    inputs_display = {
        Inputs.input_value: WorkflowInputsVellumDisplayOverrides(
            id=UUID("2268a996-bd17-4832-b3ff-f5662d54b306"), name="input-value", required=True
        )
    }
    entrypoint_displays = {
        TemplatingNode: EntrypointVellumDisplayOverrides(
            id=UUID("0bf86989-13f2-438c-ab9c-d172e5771d31"),
            edge_display=EdgeDisplay(id=UUID("38532a0e-9432-4ed2-8a34-48a29fd6984d")),
        )
    }
    edge_displays = {
        (TemplatingNode.Ports.default, FinalOutput): EdgeDisplay(id=UUID("417c56a4-cdc1-4f9d-a10c-b535163f51e8"))
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputVellumDisplayOverrides(
            id=UUID("5469b810-6ea6-4362-9e79-e360d44a1405"),
            name="final-output",
        )
    }
