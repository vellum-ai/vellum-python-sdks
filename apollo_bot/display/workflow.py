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
from ..nodes.check_tag_node import CheckTagNode
from ..nodes.create_linear_ticket_node import CreateLinearTicketNode
from ..nodes.fetch_slack_message_node import FetchSlackMessageNode
from ..nodes.final_output import FinalOutput
from ..nodes.output_linear_ticket import OutputLinearTicket
from ..nodes.output_path_taken import OutputPathTaken
from ..nodes.parse_slack_url_node import ParseSlackUrlNode
from ..nodes.reply_in_slack_node import ReplyInSlackNode
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("63884a7b-c01c-4cbc-b8d4-abe0a8796f6b"),
        entrypoint_node_source_handle_id=UUID("eba8fd73-57ab-4d7b-8f75-b54dbe5fc8ba"),
        entrypoint_node_display=NodeDisplayData(
            position=NodeDisplayPosition(x=0, y=0),
            z_index=8,
            width=124,
            height=48,
            icon="vellum:icon:right-to-bracket",
            color="stone",
        ),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-109.15611950952962, y=319.8567686578584, zoom=0.5323973167009265)
        ),
    )
    inputs_display = {
        Inputs.slack_url: WorkflowInputsDisplay(id=UUID("4d0d62f0-a56f-4bde-b407-f5164bece002"), name="slack_url")
    }
    entrypoint_displays = {
        ParseSlackUrlNode: EntrypointDisplay(
            id=UUID("63884a7b-c01c-4cbc-b8d4-abe0a8796f6b"),
            edge_display=EdgeDisplay(id=UUID("95b54dcd-5e0f-4cf4-8a3a-8dfe00badad1")),
        )
    }
    edge_displays = {
        (ParseSlackUrlNode.Ports.default, FetchSlackMessageNode): EdgeDisplay(
            id=UUID("2ff26be2-ebed-49cc-9050-991f6c83bceb"), z_index=1
        ),
        (FetchSlackMessageNode.Ports.default, CheckTagNode): EdgeDisplay(
            id=UUID("d0edda4d-d757-4b6d-8d46-08cad3ed4ab1"), z_index=2
        ),
        (CheckTagNode.Ports.not_tagged, OutputPathTaken): EdgeDisplay(
            id=UUID("b492f570-5c6e-4292-8142-11875aa1ad56"), z_index=3
        ),
        (OutputPathTaken.Ports.default, FinalOutput): EdgeDisplay(
            id=UUID("30df99af-02f6-42f2-b354-bce5362f1f78"), z_index=4
        ),
        (CheckTagNode.Ports.tagged, CreateLinearTicketNode): EdgeDisplay(
            id=UUID("f74e4795-05bc-438c-85c0-98f3ff2062d4"), z_index=5
        ),
        (CreateLinearTicketNode.Ports.default, ReplyInSlackNode): EdgeDisplay(
            id=UUID("c7f3486a-63ff-419c-81d0-0ebaa045be2f"), z_index=6
        ),
        (ReplyInSlackNode.Ports.default, OutputLinearTicket): EdgeDisplay(
            id=UUID("9aceb4b6-7842-4b0f-bbca-4ff7964d9960"), z_index=7
        ),
    }
    output_displays = {
        Workflow.Outputs.path_taken: WorkflowOutputDisplay(
            id=UUID("f04ec2cc-fd32-42b7-aac8-273bfaa3a283"), name="path_taken"
        ),
        Workflow.Outputs.linear_ticket: WorkflowOutputDisplay(
            id=UUID("79f7c63f-3378-4ab6-9355-d703036b24d4"), name="linear_ticket"
        ),
    }
