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
from ..nodes.error_node import ErrorNode
from ..nodes.final_output import FinalOutput
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
        Inputs.query: WorkflowInputsVellumDisplayOverrides(id=UUID("a6ef8809-346e-469c-beed-2e5c4e9844c5"))
    }
    entrypoint_displays = {
        ErrorNode: EntrypointVellumDisplayOverrides(
            id=UUID("27a1723c-e892-4303-bbf0-c1a0428af295"),
            edge_display=EdgeVellumDisplayOverrides(id=UUID("bcd998c4-0df4-4f59-8b15-ed1f64c5c157")),
        )
    }
    edge_displays = {
        (ErrorNode.Ports.default, FinalOutput): EdgeVellumDisplayOverrides(
            id=UUID("2fb36bc6-ac91-4aad-bb58-fbc6c95ed6e3")
        )
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputVellumDisplayOverrides(
            id=UUID("43e128f4-24fe-4484-9d08-948a4a390707"),
            node_id=UUID("ed688426-1976-4d0c-9f3a-2a0b0fae161a"),
            node_input_id=UUID("097798e5-9330-46a4-b8ec-e93532668d37"),
            name="final-output",
            label="Final Output",
            target_handle_id=UUID("b28439f6-0c1e-44c0-87b1-b7fa3c7408b2"),
            display_data=NodeDisplayData(position=NodeDisplayPosition(x=2750, y=210), width=480, height=234),
            edge_id=UUID("2fb36bc6-ac91-4aad-bb58-fbc6c95ed6e3"),
        )
    }
