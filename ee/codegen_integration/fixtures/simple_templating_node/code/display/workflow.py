from uuid import UUID

from vellum_ee.workflows.display.vellum import (
    EdgeVellumDisplayOverrides,
    EntrypointVellumDisplayOverrides,
    NodeDisplayData,
    NodeDisplayPosition,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowMetaVellumDisplayOverrides,
    WorkflowOutputVellumDisplayOverrides,
)
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay

from ..nodes.final_output import FinalOutput
from ..nodes.templating_node import TemplatingNode
from ..workflow import Workflow


class WorkflowDisplay(VellumWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaVellumDisplayOverrides(
        entrypoint_node_id=UUID("6b52893a-e649-434d-aedd-e8ad73d78dce"),
        entrypoint_node_source_handle_id=UUID("b4f25dad-17c6-464d-b347-9945065f17e4"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-992.7774269608426, y=-82.38774859214823, zoom=0.6534253694599966)
        ),
    )
    inputs_display = {}
    entrypoint_displays = {
        TemplatingNode: EntrypointVellumDisplayOverrides(
            id=UUID("6b52893a-e649-434d-aedd-e8ad73d78dce"),
            edge_display=EdgeVellumDisplayOverrides(id=UUID("662141c0-23b1-4513-9b8a-e382e56c4021")),
        )
    }
    edge_displays = {
        (TemplatingNode.Ports.default, FinalOutput): EdgeVellumDisplayOverrides(
            id=UUID("6deb7d8b-b4cc-488f-aa30-e3e5f0957882")
        )
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputVellumDisplayOverrides(
            id=UUID("b0961a8d-f702-4922-b410-2aecf7d34b68"),
            node_id=UUID("f0347fdc-1611-446c-b1da-408511d4181b"),
            node_input_id=UUID("bb465fa1-defb-493c-8284-7156cd680fb3"),
            name="final-output",
            label="Final Output",
            target_handle_id=UUID("f3ad283c-d092-4973-91e0-996e5859002a"),
            display_data=NodeDisplayData(
                position=NodeDisplayPosition(x=2752.5214681440443, y=210), width=478, height=234
            ),
            edge_id=UUID("6deb7d8b-b4cc-488f-aa30-e3e5f0957882"),
        )
    }
