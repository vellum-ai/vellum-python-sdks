from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.add_agent_message_to_chat_history import AddAgentMessageToChatHistory


class AddAgentMessageToChatHistoryDisplay(BaseTemplatingNodeDisplay[AddAgentMessageToChatHistory]):
    label = "Add Agent Message to Chat History"
    node_id = UUID("910d3a9e-2027-480b-89f2-5da266418462")
    target_handle_id = UUID("36118211-0008-42cc-823e-b35747e39ac5")
    node_input_ids_by_name = {
        "inputs.chat_history": UUID("6b197002-97c0-46f7-b250-a313e32ef33c"),
        "template": UUID("90c2edb9-9311-4a9d-9c41-32c0345c7028"),
        "inputs.message": UUID("0f55f816-6a3d-4438-9d56-f5bff0518e27"),
    }
    output_display = {
        AddAgentMessageToChatHistory.Outputs.result: NodeOutputDisplay(
            id=UUID("7293b667-9be4-4812-9e55-4b8f980cdf12"), name="result"
        )
    }
    port_displays = {
        AddAgentMessageToChatHistory.Ports.default: PortDisplayOverrides(
            id=UUID("ef6b79df-89dd-4c5a-b3fe-1bba8dc98fc3")
        )
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2025.2963688579166, y=329.8405550495836), width=459, height=283
    )
