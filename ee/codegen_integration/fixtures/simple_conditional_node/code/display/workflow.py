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
from ..nodes.conditional_node import ConditionalNode
from ..nodes.final_output import FinalOutput
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("6dbd327c-3b96-4da4-9063-5b36dab7f6d0"),
        entrypoint_node_source_handle_id=UUID("498eed8e-38d5-48b8-bbc4-f45411100502"),
        entrypoint_node_display=NodeDisplayData(
            position=NodeDisplayPosition(x=1545, y=330), width=124, height=48, z_index=None
        ),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-1285.5267112922663, y=12.259663658494276, zoom=0.7063356365705541)
        ),
    )
    inputs_display = {
        Inputs.foobar: WorkflowInputsDisplay(id=UUID("5f64210f-ec43-48ce-ae40-40a9ba4c4c11"), name="foobar"),
        Inputs.bazbaz: WorkflowInputsDisplay(id=UUID("b81c5c88-9528-47d0-8106-14a75520ed47"), name="bazbaz"),
    }
    entrypoint_displays = {
        ConditionalNode: EntrypointDisplay(
            id=UUID("6dbd327c-3b96-4da4-9063-5b36dab7f6d0"),
            edge_display=EdgeDisplay(id=UUID("549da4b2-e72a-468f-b233-34efbbae75ae")),
        )
    }
    edge_displays = {
        (ConditionalNode.Ports.branch_1, FinalOutput): EdgeDisplay(id=UUID("97779960-7685-4a9d-ba40-f748131fb4f2"))
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("d8381526-1225-4843-8c22-eec7747445e4"), name="final-output"
        )
    }
