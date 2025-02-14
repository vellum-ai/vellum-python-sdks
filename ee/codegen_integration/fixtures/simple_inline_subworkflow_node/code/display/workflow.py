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
from ..nodes.subworkflow_node import SubworkflowNode
from ..workflow import Workflow


class WorkflowDisplay(VellumWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaVellumDisplayOverrides(
        entrypoint_node_id=UUID("48134634-f654-4a45-9f00-4e9378ab1f32"),
        entrypoint_node_source_handle_id=UUID("c1eca197-d299-4feb-906b-a9f4647e759c"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-1025.2230215827337, y=107.98021582733813, zoom=0.7014388489208633)
        ),
    )
    inputs_display = {
        Inputs.query: WorkflowInputsVellumDisplayOverrides(
            id=UUID("ffa88d81-4453-4cd6-a800-a35832c0aaa7"), name="query", required=True
        )
    }
    entrypoint_displays = {
        SubworkflowNode: EntrypointVellumDisplayOverrides(
            id=UUID("48134634-f654-4a45-9f00-4e9378ab1f32"),
            edge_display=EdgeVellumDisplayOverrides(id=UUID("ff1e812c-a62d-4ab2-90cb-0f2617d2121b")),
        )
    }
    edge_displays = {
        (SubworkflowNode.Ports.default, FinalOutput): EdgeVellumDisplayOverrides(
            id=UUID("d6c3d222-a05c-43b2-8d21-462f94fd3b1e")
        )
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputVellumDisplayOverrides(
            id=UUID("b38e08c7-904d-4f49-b8fb-56e1eff254d6"), name="final-output"
        )
    }
