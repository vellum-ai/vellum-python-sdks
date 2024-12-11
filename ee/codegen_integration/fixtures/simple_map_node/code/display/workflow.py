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
from ..nodes.map_node import MapNode
from ..workflow import Workflow


class WorkflowDisplay(VellumWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaVellumDisplayOverrides(
        entrypoint_node_id=UUID("77325e35-b73e-4596-bfb0-3cf3ddf11a2e"),
        entrypoint_node_source_handle_id=UUID("f342d075-e79a-46ea-8de9-e40ed8152070"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=0, y=151.5), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=224.90864867521066, y=180.0534988628682, zoom=0.6573565995604552)
        ),
    )
    inputs_display = {
        Inputs.items: WorkflowInputsVellumDisplayOverrides(
            id=UUID("cdc4468f-45e7-46ce-bbe7-d1aa9ad86514"), required=True
        )
    }
    entrypoint_displays = {
        MapNode: EntrypointVellumDisplayOverrides(
            id=UUID("77325e35-b73e-4596-bfb0-3cf3ddf11a2e"),
            edge_display=EdgeVellumDisplayOverrides(id=UUID("ea7f1340-eeb4-448c-91eb-8b0e36bef447")),
        )
    }
    edge_displays = {
        (MapNode.Ports.default, FinalOutput): EdgeVellumDisplayOverrides(
            id=UUID("2e2e5cdc-94be-4df2-9e00-23467e2ea209")
        )
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputVellumDisplayOverrides(
            id=UUID("d9269719-a7a2-4388-9b85-73e329a78d16"),
            node_id=UUID("fa0d5829-f259-4db8-a11a-b12fd7237ea5"),
            node_input_id=UUID("ca8f8a34-24d3-4941-893f-73c5e3bbb66c"),
            name="final-output",
            label="Final Output",
            target_handle_id=UUID("8e19172a-4f87-4c21-8c91-ccdfb3e74c16"),
            display_data=NodeDisplayData(position=NodeDisplayPosition(x=864, y=58.5), width=454, height=234),
            edge_id=UUID("2e2e5cdc-94be-4df2-9e00-23467e2ea209"),
        )
    }
