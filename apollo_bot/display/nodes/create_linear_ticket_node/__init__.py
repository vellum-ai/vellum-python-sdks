from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ....nodes.create_linear_ticket_node import CreateLinearTicketNode


class CreateLinearTicketNodeDisplay(BaseNodeDisplay[CreateLinearTicketNode]):
    label = "CreateLinearTicketNode"
    node_id = UUID("22f65490-f3cf-4c39-83a3-3afaac0d94b6")
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2198, y=245), z_index=14, icon="vellum:icon:wrench", color="teal"
    )
    attribute_ids_by_name = {
        "ml_model": UUID("9abc541a-9b00-4932-ae57-1b756fdb0020"),
        "blocks": UUID("696c1e64-6fd3-4334-8d66-d0623c3ef745"),
        "prompt_inputs": UUID("24afc650-2eaa-4b42-b11b-c3b18248d2cb"),
        "parameters": UUID("dce212a8-b9e6-4b35-8264-ece56f32477b"),
        "functions": UUID("52eb7b9e-8c44-4491-9a52-cbc903419898"),
        "max_prompt_iterations": UUID("d3298c02-604d-4d91-8e00-875b954ff5b7"),
        "settings": UUID("cf2afe44-6aab-438a-9a6e-3fff021d2757"),
    }
    output_display = {
        CreateLinearTicketNode.Outputs.text: NodeOutputDisplay(
            id=UUID("4328f2a4-5dae-41b2-8d0f-5d65fcfb4589"), name="text"
        ),
        CreateLinearTicketNode.Outputs.chat_history: NodeOutputDisplay(
            id=UUID("14d1a62d-56e3-439e-994f-6e806fd2c32a"), name="chat_history"
        ),
    }
    port_displays = {
        CreateLinearTicketNode.Ports.default: PortDisplayOverrides(id=UUID("1d687372-c2a5-4fcf-b55c-cbad5fa9b306"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2198, y=245), z_index=14, icon="vellum:icon:wrench", color="teal"
    )
