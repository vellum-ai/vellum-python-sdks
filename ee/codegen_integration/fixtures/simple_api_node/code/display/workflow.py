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
from ..nodes.api_node import ApiNode
from ..nodes.final_output import FinalOutput
from ..workflow import Workflow


class WorkflowDisplay(VellumWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaVellumDisplayOverrides(
        entrypoint_node_id=UUID("c4ef480d-635a-49c8-900f-6583c4b79fb5"),
        entrypoint_node_source_handle_id=UUID("0465edea-e797-4558-aabb-65bce040e095"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-1047.2625054371465, y=194.66659417137888, zoom=0.7166159199652022)
        ),
    )
    inputs_display = {
        Inputs.foo: WorkflowInputsVellumDisplayOverrides(id=UUID("c6f392da-bd3a-40ba-8fdd-75fc36b18fd8"), required=True)
    }
    entrypoint_displays = {
        ApiNode: EntrypointVellumDisplayOverrides(
            id=UUID("c4ef480d-635a-49c8-900f-6583c4b79fb5"),
            edge_display=EdgeVellumDisplayOverrides(id=UUID("8fbc728e-7408-4456-a932-001423ae8efa")),
        )
    }
    edge_displays = {
        (ApiNode.Ports.default, FinalOutput): EdgeVellumDisplayOverrides(
            id=UUID("dc149e06-f71f-48ba-be58-0c3f6be13719")
        )
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputVellumDisplayOverrides(
            id=UUID("e53bdfb1-f74d-43f0-a3fc-24c7a5162a62"),
            node_id=UUID("dad01b99-c0b4-4904-a75e-066fa947d256"),
            node_input_id=UUID("bc3e4cad-e6b6-4f3d-b0d8-ee7099fe6352"),
            name="final-output",
            label="Final Output",
            target_handle_id=UUID("2d005e2b-e8bb-404a-9702-8faf10c2213d"),
            display_data=NodeDisplayData(position=NodeDisplayPosition(x=2750, y=210), width=467, height=234),
            edge_id=UUID("dc149e06-f71f-48ba-be58-0c3f6be13719"),
        )
    }
