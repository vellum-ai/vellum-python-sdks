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
from ..nodes.tool_calling_node_1 import ToolCallingNode
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("732f8d98-896c-4412-a02c-862200fcd8af"),
        entrypoint_node_source_handle_id=UUID("afd7816c-ddc4-4e89-8e3c-0c0bd393a8df"),
        entrypoint_node_display=NodeDisplayData(
            position=NodeDisplayPosition(x=1162.3642159363746, y=-46.14180491908928), width=124, height=48
        ),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-259.91736965568896, y=400.5028799868387, zoom=0.3002218483801739)
        ),
    )
    inputs_display = {
        Inputs.chat_history: WorkflowInputsDisplay(
            id=UUID("b261e76e-ae85-4902-b32f-3a98c41f8c49"), name="chat_history", color="tomato"
        )
    }
    entrypoint_displays = {
        ToolCallingNode: EntrypointDisplay(
            id=UUID("732f8d98-896c-4412-a02c-862200fcd8af"),
            edge_display=EdgeDisplay(id=UUID("69d8a3ed-5f5e-46fc-913f-5eb8771607f6")),
        )
    }
    edge_displays = {
        (ToolCallingNode.Ports.default, FinalOutput): EdgeDisplay(id=UUID("2b584376-65a0-415c-a8d9-0a35f8765e6c"))
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("53a3b97c-461e-4441-a513-36a8545a20cd"), name="final-output"
        )
    }
