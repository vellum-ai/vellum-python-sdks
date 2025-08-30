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
from ..nodes.add_image_to_chat_history import AddImageToChatHistory
from ..nodes.extract_by_chat_history import ExtractByChatHistory
from ..nodes.extract_by_document_url import ExtractByDocumentURL
from ..nodes.final_output import FinalOutput
from ..nodes.final_output_6 import FinalOutput6
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("a7f0df51-cd51-45e5-a8ec-5c01e4a62859"),
        entrypoint_node_source_handle_id=UUID("d0976f57-bece-4eb5-8629-e845f0b9c7f9"),
        entrypoint_node_display=NodeDisplayData(
            position=NodeDisplayPosition(x=-55.26644635815683, y=510.7385521062415), width=124, height=48
        ),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=257.17303389015467, y=185.5531574161448, zoom=0.35565791828925275)
        ),
    )
    inputs_display = {
        Inputs.image_url: WorkflowInputsDisplay(id=UUID("5be00b19-5016-4e16-93b3-980a6f8838ad"), name="image_url"),
        Inputs.workflow_input_chat_history: WorkflowInputsDisplay(
            id=UUID("ae1eb3ce-4b1d-40ee-936f-308f1062a4fd"), name="workflow_input_chat_history", color="pink"
        ),
    }
    entrypoint_displays = {
        ExtractByChatHistory: EntrypointDisplay(
            id=UUID("a7f0df51-cd51-45e5-a8ec-5c01e4a62859"),
            edge_display=EdgeDisplay(id=UUID("d3eb566f-f1c0-4f79-bebe-b2bb89ed9910")),
        ),
        AddImageToChatHistory: EntrypointDisplay(
            id=UUID("a7f0df51-cd51-45e5-a8ec-5c01e4a62859"),
            edge_display=EdgeDisplay(id=UUID("e8571392-39cf-4ba1-8325-7ccf64996170")),
        ),
    }
    edge_displays = {
        (ExtractByDocumentURL.Ports.default, FinalOutput): EdgeDisplay(id=UUID("30eb4c90-c436-4181-99d5-d91f108b0477")),
        (ExtractByChatHistory.Ports.default, FinalOutput6): EdgeDisplay(
            id=UUID("b92b2e32-930a-4e51-afdd-9e1ce5a0a23a")
        ),
        (AddImageToChatHistory.Ports.default, ExtractByDocumentURL): EdgeDisplay(
            id=UUID("f2f4eb15-20a3-4024-9fbb-84e35a531405")
        ),
    }
    output_displays = {
        Workflow.Outputs.final_output_6: WorkflowOutputDisplay(
            id=UUID("4dfe9122-354b-4796-a2de-4eaa38a0c5df"), name="final-output-6"
        ),
        Workflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("9c3830c9-7faa-4872-83e5-7360f662f8e2"), name="final-output"
        ),
    }
