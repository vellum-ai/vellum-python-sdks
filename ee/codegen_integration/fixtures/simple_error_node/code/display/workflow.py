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
)
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay

from ..inputs import Inputs
from ..nodes.error_node import ErrorNode
from ..workflow import Workflow


class WorkflowDisplay(VellumWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaVellumDisplayOverrides(
        entrypoint_node_id=UUID("27a1723c-e892-4303-bbf0-c1a0428af295"),
        entrypoint_node_source_handle_id=UUID("6cbf47ee-84ef-42cb-b1df-7b9e0fee2bee"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-1138.021580793094, y=-98.75478823846774, zoom=0.7790666306986781)
        ),
    )
    inputs_display = {
        Inputs.custom_error: WorkflowInputsVellumDisplayOverrides(
            id=UUID("a6ef8809-346e-469c-beed-2e5c4e9844c5"), required=True
        )
    }
    entrypoint_displays = {
        ErrorNode: EntrypointVellumDisplayOverrides(
            id=UUID("27a1723c-e892-4303-bbf0-c1a0428af295"),
            edge_display=EdgeVellumDisplayOverrides(id=UUID("bcd998c4-0df4-4f59-8b15-ed1f64c5c157")),
        )
    }
    output_displays = {}
