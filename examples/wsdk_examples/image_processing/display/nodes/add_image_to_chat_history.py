from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.add_image_to_chat_history import AddImageToChatHistory


class AddImageToChatHistoryDisplay(BaseTemplatingNodeDisplay[AddImageToChatHistory]):
    label = "Add Image to Chat History"
    node_id = UUID("94cda50f-0846-4724-bb0d-009c743cc167")
    target_handle_id = UUID("56355ee9-fd7e-481c-99a2-48254f862f7f")
    node_input_ids_by_name = {
        "inputs.chat_history": UUID("156eb216-6699-499e-8aac-9df98e54d14e"),
        "template": UUID("d75eba1c-ce79-4921-a0d8-579bc60975b6"),
        "inputs.image_url": UUID("fc0d002f-be41-4241-b67d-4f66a39d20a1"),
    }
    output_display = {
        AddImageToChatHistory.Outputs.result: NodeOutputDisplay(
            id=UUID("b7b64225-95f6-4a51-8a91-048eef1a5b13"), name="result"
        )
    }
    port_displays = {
        AddImageToChatHistory.Ports.default: PortDisplayOverrides(id=UUID("508eec8f-bf3a-40a7-b47f-7e393b7f0672"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=282.3228076068352, y=552.4516595338625),
        width=459,
        height=387,
        comment=NodeDisplayComment(expanded=True),
    )
