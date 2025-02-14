from uuid import UUID

from vellum_ee.workflows.display.vellum import (
    EdgeVellumDisplayOverrides,
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
from ..nodes.subworkflow_deployment import SubworkflowDeployment
from ..workflow import Workflow


class WorkflowDisplay(VellumWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaVellumDisplayOverrides(
        entrypoint_node_id=UUID("39a5155a-d137-4a56-be36-d525802df463"),
        entrypoint_node_source_handle_id=UUID("beddfefc-dc34-483d-b313-f6a2a2e0737e"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-1404.2954545454543, y=51.525595763459876, zoom=0.7965578111209178)
        ),
    )
    inputs_display = {
        Inputs.test: WorkflowInputsVellumDisplayOverrides(
            id=UUID("93b9d3fb-251c-4a53-a1d5-4bd8e61947c5"), name="test", required=True
        )
    }
    entrypoint_displays = {
        SubworkflowDeployment: EntrypointVellumDisplayOverrides(
            id=UUID("39a5155a-d137-4a56-be36-d525802df463"),
            edge_display=EdgeVellumDisplayOverrides(id=UUID("fbf75594-70e8-4e03-ae3d-a64f573df51f")),
        )
    }
    edge_displays = {
        (SubworkflowDeployment.Ports.default, FinalOutput): EdgeVellumDisplayOverrides(
            id=UUID("85970a9b-4ce7-46a5-b539-66aaeef080df")
        )
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputVellumDisplayOverrides(
            id=UUID("4dc6e13e-92ba-436e-aa35-87e258f2f585"),
            name="final-output",
        )
    }
