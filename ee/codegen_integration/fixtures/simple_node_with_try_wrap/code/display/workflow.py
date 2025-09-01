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
from ..nodes.final_output import FinalOutput
from ..nodes.prompt_node import PromptNode
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("1c05df03-f699-42e4-9816-9b1b3757c10e"),
        entrypoint_node_source_handle_id=UUID("4ee49c3a-68ef-4134-b73d-c1754abaac44"),
        entrypoint_node_display=NodeDisplayData(
            position=NodeDisplayPosition(x=1545, y=330), width=124, height=48, z_index=None
        ),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-1299.4246406540078, y=142.4751202622371, zoom=0.8897129183403404)
        ),
    )
    inputs_display = {
        Inputs.input: WorkflowInputsDisplay(id=UUID("2915dbdd-c4fa-4b52-a35c-11625bb47cbf"), name="input")
    }
    entrypoint_displays = {
        PromptNode: EntrypointDisplay(
            id=UUID("1c05df03-f699-42e4-9816-9b1b3757c10e"),
            edge_display=EdgeDisplay(id=UUID("d56e2ecf-5a82-4e37-879c-531fdecf12f6")),
        )
    }
    edge_displays = {
        (PromptNode.Ports.default, FinalOutput): EdgeDisplay(id=UUID("95b7bf4b-6447-438a-88a5-1f47ec9b3d3c"))
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("f1eca494-a7dc-41c0-9c74-9658a64955e6"), name="final-output"
        )
    }
