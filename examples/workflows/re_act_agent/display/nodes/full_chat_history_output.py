from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.full_chat_history_output import FullChatHistoryOutput


class FullChatHistoryOutputDisplay(BaseFinalOutputNodeDisplay[FullChatHistoryOutput]):
    label = "Full Chat History Output"
    node_id = UUID("d0668a5a-4b7e-4dfe-842c-d041e512a996")
    target_handle_id = UUID("0d45a6a1-0079-4424-9411-74d19a05d772")
    output_name = "full-chat-history"
    node_input_ids_by_name = {"node_input": UUID("5b2ddce3-6405-4468-948c-0eb664eda821")}
    output_display = {
        FullChatHistoryOutput.Outputs.value: NodeOutputDisplay(
            id=UUID("b6effd4f-662d-4cae-9847-9598f3898660"), name="value"
        )
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=3405, y=900), width=456, height=239)
