from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseCodeExecutionNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.accumulate_chat_history import AccumulateChatHistory


class AccumulateChatHistoryDisplay(BaseCodeExecutionNodeDisplay[AccumulateChatHistory]):
    label = "Accumulate Chat History"
    node_id = UUID("58afeee4-346a-46fa-8097-91ba86682de9")
    target_handle_id = UUID("556825c6-f00c-4dd1-883f-2d7ddb9286c0")
    output_id = UUID("e446171c-840f-4e13-b404-92d98f745cbe")
    log_output_id = UUID("56184319-1a54-4373-9cbc-b7c298d1a33c")
    node_input_ids_by_name = {
        "code_inputs.invoked_functions": UUID("40efed5b-3322-45f4-8bb3-15387fd0b35c"),
        "code_inputs.assistant_message": UUID("0437c3cb-dbf3-4ee2-812b-7171cf3599d0"),
        "code_inputs.current_chat_history": UUID("49f7dd2f-3f26-41c3-b018-cb412db7d668"),
        "code": UUID("a5b4dbd2-a3cf-46d3-a74d-ed2acb1293ba"),
        "runtime": UUID("8a9822ac-f11a-4fec-bbe0-c1b48870c404"),
    }
    output_display = {
        AccumulateChatHistory.Outputs.result: NodeOutputDisplay(
            id=UUID("e446171c-840f-4e13-b404-92d98f745cbe"), name="result"
        ),
        AccumulateChatHistory.Outputs.log: NodeOutputDisplay(
            id=UUID("56184319-1a54-4373-9cbc-b7c298d1a33c"), name="log"
        ),
    }
    port_displays = {
        AccumulateChatHistory.Ports.default: PortDisplayOverrides(id=UUID("3f9d53b9-5f34-4021-8d33-18c90af361a6"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3988.7945432054958, y=130.58593157958728), width=456, height=378
    )
