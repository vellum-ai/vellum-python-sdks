from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.summarize_image_by_url_chat_history import SummarizeImageByURLChatHistory


class SummarizeImageByURLChatHistoryDisplay(BaseInlinePromptNodeDisplay[SummarizeImageByURLChatHistory]):
    label = "Summarize Image by URL -> Chat History"
    node_id = UUID("92b90a99-61b3-4ec9-aded-114366fb5d6b")
    output_id = UUID("26238951-f3b6-454c-81c6-1a6f7da20919")
    array_output_id = UUID("9b21a9dd-2515-46d9-84a0-c0ef59890b18")
    target_handle_id = UUID("0340e04b-13ff-4698-9fd4-8fdac3d4920d")
    node_input_ids_by_name = {"chat_history": UUID("9cde4b6f-77c6-47e7-963d-ea0a903c81b8")}
    output_display = {
        SummarizeImageByURLChatHistory.Outputs.text: NodeOutputDisplay(
            id=UUID("26238951-f3b6-454c-81c6-1a6f7da20919"), name="text"
        ),
        SummarizeImageByURLChatHistory.Outputs.results: NodeOutputDisplay(
            id=UUID("9b21a9dd-2515-46d9-84a0-c0ef59890b18"), name="results"
        ),
        SummarizeImageByURLChatHistory.Outputs.json: NodeOutputDisplay(
            id=UUID("f420b0a1-bcb4-4bbc-b7c4-5ffb9e108c4f"), name="json"
        ),
    }
    port_displays = {
        SummarizeImageByURLChatHistory.Ports.default: PortDisplayOverrides(
            id=UUID("8779d3ec-9211-414d-9af3-631ad3167b1d")
        )
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=837.4721057480847, y=667.4771042124831), width=480, height=175
    )
