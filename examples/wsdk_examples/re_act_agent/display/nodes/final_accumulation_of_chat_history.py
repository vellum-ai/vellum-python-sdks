from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseCodeExecutionNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.final_accumulation_of_chat_history import FinalAccumulationOfChatHistory


class FinalAccumulationOfChatHistoryDisplay(BaseCodeExecutionNodeDisplay[FinalAccumulationOfChatHistory]):
    label = "Final Accumulation of Chat History"
    node_id = UUID("124a993f-3e4f-4828-98a1-2740e2c9e399")
    target_handle_id = UUID("a0a79d87-431b-49b4-a03a-f0e20c12d888")
    output_id = UUID("f6d85d94-a58e-403d-964f-b88a44ce72f4")
    log_output_id = UUID("00f82678-ed0c-4482-8e78-f314109d571e")
    node_input_ids_by_name = {
        "code_inputs.current_chat_history": UUID("5341a54b-f04a-4dad-bfdc-11ee9fb416bd"),
        "code_inputs.assistant_message": UUID("2eb6cb8b-5065-45d7-b4a6-4faaf148b270"),
        "code": UUID("b8cf9cdb-f52e-48ed-92f7-99ff1eb77760"),
        "runtime": UUID("f6b3adda-f87d-443b-9a97-2a624c478a40"),
    }
    output_display = {
        FinalAccumulationOfChatHistory.Outputs.result: NodeOutputDisplay(
            id=UUID("f6d85d94-a58e-403d-964f-b88a44ce72f4"), name="result"
        ),
        FinalAccumulationOfChatHistory.Outputs.log: NodeOutputDisplay(
            id=UUID("00f82678-ed0c-4482-8e78-f314109d571e"), name="log"
        ),
    }
    port_displays = {
        FinalAccumulationOfChatHistory.Ports.default: PortDisplayOverrides(
            id=UUID("5f1c1a04-ec5b-449f-a2bb-c3ff93a96063")
        )
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2820, y=825), width=453, height=324)
