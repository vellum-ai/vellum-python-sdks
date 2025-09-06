from uuid import UUID

from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EntrypointDisplay,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowInputsDisplay,
    WorkflowMetaDisplay,
    WorkflowOutputDisplay,
)
from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay

from ..inputs import Inputs
from ..nodes.api_node import ApiNode
from ..nodes.final_output import FinalOutput
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("c4ef480d-635a-49c8-900f-6583c4b79fb5"),
        entrypoint_node_source_handle_id=UUID("0465edea-e797-4558-aabb-65bce040e095"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-1047.2625054371465, y=194.66659417137888, zoom=0.7166159199652022)
        ),
    )
    inputs_display = {Inputs.foo: WorkflowInputsDisplay(id=UUID("c6f392da-bd3a-40ba-8fdd-75fc36b18fd8"), name="foo")}
    entrypoint_displays = {
        ApiNode: EntrypointDisplay(
            id=UUID("c4ef480d-635a-49c8-900f-6583c4b79fb5"),
            edge_display=EdgeDisplay(id=UUID("8fbc728e-7408-4456-a932-001423ae8efa")),
        )
    }
    edge_displays = {
        (ApiNode.Ports.default, FinalOutput): EdgeDisplay(id=UUID("dc149e06-f71f-48ba-be58-0c3f6be13719"), z_index=None)
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("e53bdfb1-f74d-43f0-a3fc-24c7a5162a62"), name="final-output"
        )
    }
