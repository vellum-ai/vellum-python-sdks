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
from ..nodes.prompt_node import PromptNode
from ..workflow import Workflow


class WorkflowDisplay(VellumWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaVellumDisplayOverrides(
        entrypoint_node_id=UUID("1c05df03-f699-42e4-9816-9b1b3757c10e"),
        entrypoint_node_source_handle_id=UUID("4ee49c3a-68ef-4134-b73d-c1754abaac44"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-1299.4246406540078, y=142.4751202622371, zoom=0.8897129183403404)
        ),
    )
    inputs_display = {
        Inputs.input: WorkflowInputsVellumDisplayOverrides(
            id=UUID("2915dbdd-c4fa-4b52-a35c-11625bb47cbf"), name="input", required=False
        )
    }
    entrypoint_displays = {
        PromptNode: EntrypointVellumDisplayOverrides(
            id=UUID("1c05df03-f699-42e4-9816-9b1b3757c10e"),
            edge_display=EdgeVellumDisplayOverrides(id=UUID("d56e2ecf-5a82-4e37-879c-531fdecf12f6")),
        )
    }
    edge_displays = {
        (PromptNode.Ports.default, FinalOutput): EdgeVellumDisplayOverrides(
            id=UUID("95b7bf4b-6447-438a-88a5-1f47ec9b3d3c")
        )
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputVellumDisplayOverrides(
            id=UUID("f1eca494-a7dc-41c0-9c74-9658a64955e6"),
            node_id=UUID("54803ff7-9afd-4eb1-bff3-242345d3443d"),
            name="final-output",
            label="Final Output",
            target_handle_id=UUID("6bf50c29-d2f5-4a4f-a63b-907c9053833d"),
            display_data=NodeDisplayData(
                position=NodeDisplayPosition(x=2761.0242006615217, y=208.9757993384785), width=474, height=234
            ),
            edge_id=UUID("95b7bf4b-6447-438a-88a5-1f47ec9b3d3c"),
        )
    }
