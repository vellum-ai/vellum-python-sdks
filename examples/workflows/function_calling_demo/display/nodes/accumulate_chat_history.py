from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseCodeExecutionNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.accumulate_chat_history import AccumulateChatHistory


class AccumulateChatHistoryDisplay(BaseCodeExecutionNodeDisplay[AccumulateChatHistory]):
    label = "Accumulate Chat History"
    node_id = UUID("4787115e-23b9-4980-bf51-655da351d9e7")
    target_handle_id = UUID("6456c31d-1631-46d3-aaed-bbcad9e9be62")
    output_id = UUID("9e6d85b4-6941-4758-9304-99b94122868d")
    log_output_id = UUID("60c8dade-d9a9-441a-8997-e77afc7ec38d")
    node_input_ids_by_name = {
        "code_inputs.tool_id": UUID("eab3c9f4-78ef-4b16-afa8-dcdeffcd5af2"),
        "code_inputs.function_result": UUID("29e037ad-b6e4-40ec-a816-2fce11671f04"),
        "code": UUID("c5dc64de-d70e-4b99-a15f-0cf2c853a856"),
        "runtime": UUID("b7a6a274-756e-4983-93d4-93e4c8ee2a9b"),
        "code_inputs.assistant_message": UUID("8f59e730-6da8-4418-b5d7-e001e3b1869b"),
        "code_inputs.current_chat_history": UUID("92f43842-3d2e-47e4-8fc2-1fc62391a72c"),
    }
    output_display = {
        AccumulateChatHistory.Outputs.result: NodeOutputDisplay(
            id=UUID("9e6d85b4-6941-4758-9304-99b94122868d"), name="result"
        ),
        AccumulateChatHistory.Outputs.log: NodeOutputDisplay(
            id=UUID("60c8dade-d9a9-441a-8997-e77afc7ec38d"), name="log"
        ),
    }
    port_displays = {
        AccumulateChatHistory.Ports.default: PortDisplayOverrides(id=UUID("66a7143a-15c6-4f85-9b0b-029653f488ff"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=5700, y=-45), width=449, height=381)
