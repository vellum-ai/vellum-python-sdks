from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.chatbot_node import ChatbotNode


class ChatbotNodeDisplay(BaseNodeDisplay[ChatbotNode]):
    label = "Chatbot Node"
    node_id = UUID("7942ba5c-8ee8-4cc1-b874-5f507b6bcde3")
    output_id = UUID("b0576132-7ba5-43c5-a1ea-ce2d5d4481f4")
    array_output_id = UUID("544bfe12-533f-490b-a52e-ac8bdaf36de3")
    target_handle_id = UUID("6db9276e-5b25-462f-9c46-3fb424b19c55")
    node_input_ids_by_name = {"user_message": UUID("30d7e433-1f2e-488a-8252-3e7eee891704")}
    attribute_ids_by_name = {}
    output_display = {
        ChatbotNode.Outputs.conversation_history: NodeOutputDisplay(
            id=UUID("b0576132-7ba5-43c5-a1ea-ce2d5d4481f4"), name="conversation_history"
        ),
    }
    port_displays = {ChatbotNode.Ports.default: PortDisplayOverrides(id=UUID("cbd12458-a79a-4fa1-8a63-b06bef37b5d6"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=200, y=-50),
        width=554,
        height=456,
        comment=NodeDisplayComment(expanded=True, value="A simple chatbot node that only manages state."),
    )
