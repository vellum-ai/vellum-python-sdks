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
        entrypoint_node_id=UUID("fedbe8f4-aa63-405b-aefa-0e40e65d547e"),
        entrypoint_node_source_handle_id=UUID("4d6a6de9-d3d6-4b8f-9a71-caf53c2f31c3"),
        entrypoint_node_display=NodeDisplayData(
            position=NodeDisplayPosition(x=1545, y=330), width=124, height=48, z_index=None
        ),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-1299.4246406540078, y=142.4751202622371, zoom=0.8897129183403404)
        ),
    )
    inputs_display = {Inputs.text: WorkflowInputsDisplay(id=UUID("90c6afd3-06cc-430d-aed1-35937c062531"), name="text")}
    entrypoint_displays = {
        PromptNode: EntrypointDisplay(
            id=UUID("fedbe8f4-aa63-405b-aefa-0e40e65d547e"),
            edge_display=EdgeDisplay(id=UUID("52729326-646f-454e-8940-d8d65e659d0a")),
        )
    }
    edge_displays = {
        (PromptNode.Ports.default, FinalOutput): EdgeDisplay(id=UUID("6afd37dc-47f1-4b99-b1cc-47ff6128247b"))
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("aed7279d-59cd-4c15-b82c-21de48129ba3"), name="final-output"
        )
    }
