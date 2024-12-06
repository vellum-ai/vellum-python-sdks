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
        entrypoint_node_id=UUID("fedbe8f4-aa63-405b-aefa-0e40e65d547e"),
        entrypoint_node_source_handle_id=UUID("4d6a6de9-d3d6-4b8f-9a71-caf53c2f31c3"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-1299.4246406540078, y=142.4751202622371, zoom=0.8897129183403404)
        ),
    )
    inputs_display = {
        Inputs.text: WorkflowInputsVellumDisplayOverrides(
            id=UUID("90c6afd3-06cc-430d-aed1-35937c062531"), required=True
        )
    }
    entrypoint_displays = {
        PromptNode: EntrypointVellumDisplayOverrides(
            id=UUID("fedbe8f4-aa63-405b-aefa-0e40e65d547e"),
            edge_display=EdgeVellumDisplayOverrides(id=UUID("52729326-646f-454e-8940-d8d65e659d0a")),
        )
    }
    edge_displays = {
        (PromptNode.Ports.default, FinalOutput): EdgeVellumDisplayOverrides(
            id=UUID("6afd37dc-47f1-4b99-b1cc-47ff6128247b")
        )
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputVellumDisplayOverrides(
            id=UUID("aed7279d-59cd-4c15-b82c-21de48129ba3"),
            node_id=UUID("e39c8f13-d59b-49fc-8c59-03ee7997b9b6"),
            node_input_id=UUID("cfed56e1-bdf8-4e17-a0f9-ff1bb8ca4221"),
            name="final-output",
            label="Final Output",
            target_handle_id=UUID("77ab6d0c-7fea-441e-8e22-7afc62b3555b"),
            display_data=NodeDisplayData(
                position=NodeDisplayPosition(x=2761.0242006615217, y=208.9757993384785), width=474, height=234
            ),
            edge_id=UUID("6afd37dc-47f1-4b99-b1cc-47ff6128247b"),
        )
    }
