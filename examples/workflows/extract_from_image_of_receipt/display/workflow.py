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
from ..nodes.data_extractor import DataExtractor
from ..nodes.final_output import FinalOutput
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("6343c92f-e900-41aa-8efa-a0ddabf62d42"),
        entrypoint_node_source_handle_id=UUID("c30f3ded-6947-4206-a443-21bbfef379c1"),
        entrypoint_node_display=NodeDisplayData(
            position=NodeDisplayPosition(x=604.6530102688362, y=-81.4120252975955), width=124, height=48
        ),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-211.11940130297864, y=393.24473293335495, zoom=0.39997596956099407)
        ),
    )
    inputs_display = {
        Inputs.chat_history: WorkflowInputsDisplay(id=UUID("cda43bd1-2f3f-449e-93bc-e3e4a7be87ba"), name="chat_history")
    }
    entrypoint_displays = {
        DataExtractor: EntrypointDisplay(
            id=UUID("6343c92f-e900-41aa-8efa-a0ddabf62d42"),
            edge_display=EdgeDisplay(id=UUID("735a5360-63f7-4420-8ca0-9bb95d0f4b01")),
        )
    }
    edge_displays = {
        (DataExtractor.Ports.default, FinalOutput): EdgeDisplay(id=UUID("74c32f43-a8b2-4549-8189-c5b5eaad1862"))
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("dfa69d72-3f2a-4f56-b639-5f0331ed5dc5"), name="final-output"
        )
    }
