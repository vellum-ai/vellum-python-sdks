from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.add_image_to_chat_history import AddImageToChatHistory


class AddImageToChatHistoryDisplay(BaseTemplatingNodeDisplay[AddImageToChatHistory]):
    label = "Add Image to Chat History"
    node_id = UUID("cee9404a-f77d-4011-a6d0-b764dc6465a6")
    target_handle_id = UUID("35ba823b-e0cd-4b5e-84a6-07c63ae3e34e")
    node_input_ids_by_name = {
        "inputs.chat_history": UUID("0f373af9-1521-4cd2-b29d-222a375b02da"),
        "template": UUID("33443abf-6804-4ffc-99e4-14341d889303"),
        "inputs.image_url": UUID("7ce37d39-0f62-4878-a7c4-435f94118b51"),
    }
    output_display = {
        AddImageToChatHistory.Outputs.result: NodeOutputDisplay(
            id=UUID("d1d37e2e-4bff-498b-a191-c8b72f224f75"), name="result"
        )
    }
    port_displays = {
        AddImageToChatHistory.Ports.default: PortDisplayOverrides(id=UUID("24102683-8533-4a10-bebd-10e138293da4"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=282.3228076068352, y=552.4516595338625),
        width=457,
        height=350,
        comment=NodeDisplayComment(expanded=True),
    )
