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
from ..nodes.final_output import FinalOutput
from ..nodes.final_output_6 import FinalOutput6
from ..nodes.summarize_image_by_chat_history import SummarizeImageByChatHistory
from ..nodes.summarize_image_by_url_chat_history import SummarizeImageByURLChatHistory
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("374eff56-51f2-4432-a642-ea35d9fbc455"),
        entrypoint_node_source_handle_id=UUID("061a80b9-549b-441c-a623-21038cddeb6f"),
        entrypoint_node_display=NodeDisplayData(
            position=NodeDisplayPosition(x=-55.26644635815683, y=510.7385521062415), width=124, height=48
        ),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-52.35286997670073, y=75.59489590281208, zoom=0.7571471902081293)
        ),
    )
    inputs_display = {
        Inputs.image_url: WorkflowInputsDisplay(id=UUID("48d08975-862a-4858-9659-adf59f6648cc"), name="image_url"),
        Inputs.workflow_input_chat_history: WorkflowInputsDisplay(
            id=UUID("fb7211bb-0f6d-4176-a104-06c2261ebd5c"), name="workflow_input_chat_history", color="pink"
        ),
    }
    entrypoint_displays = {
        SummarizeImageByChatHistory: EntrypointDisplay(
            id=UUID("374eff56-51f2-4432-a642-ea35d9fbc455"),
            edge_display=EdgeDisplay(id=UUID("5f4e4e51-9316-4b5b-8704-bcba917e92af")),
        ),
        AddImageToChatHistory: EntrypointDisplay(
            id=UUID("374eff56-51f2-4432-a642-ea35d9fbc455"),
            edge_display=EdgeDisplay(id=UUID("6dac810b-ac0c-431a-ae93-19eaa75253c3")),
        ),
    }
    edge_displays = {
        (SummarizeImageByURLChatHistory.Ports.default, FinalOutput): EdgeDisplay(
            id=UUID("04f83166-36b5-4f1f-84cd-c5e327d3954a")
        ),
        (SummarizeImageByChatHistory.Ports.default, FinalOutput6): EdgeDisplay(
            id=UUID("f2e51a46-f977-4d99-a4b2-002593921cdf")
        ),
        (AddImageToChatHistory.Ports.default, SummarizeImageByURLChatHistory): EdgeDisplay(
            id=UUID("f92e9611-8bbd-45df-80a5-3652edb6d3b6")
        ),
    }
    output_displays = {
        Workflow.Outputs.final_output_6: WorkflowOutputDisplay(
            id=UUID("92f6b627-7e91-49d1-9f26-4fb139a7f9a9"), name="final-output-6"
        ),
        Workflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("3ae9132d-cbb9-4237-ac5b-9c80096eaac5"), name="final-output"
        ),
    }
