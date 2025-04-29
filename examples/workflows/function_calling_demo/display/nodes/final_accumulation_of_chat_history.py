from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseCodeExecutionNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.final_accumulation_of_chat_history import FinalAccumulationOfChatHistory


class FinalAccumulationOfChatHistoryDisplay(BaseCodeExecutionNodeDisplay[FinalAccumulationOfChatHistory]):
    label = "Final Accumulation of Chat History"
    node_id = UUID("d1855d88-8316-4377-8e95-9395c8f75855")
    target_handle_id = UUID("92fc3b35-8e45-473f-ba98-c7664714c1f9")
    output_id = UUID("1c8268a2-4e31-4fd5-b493-0a9f28b7ec19")
    log_output_id = UUID("a97f5cbf-3a00-4af7-921d-c553c8b3243f")
    node_input_ids_by_name = {
        "code": UUID("ec9748c7-a43c-4a94-9772-ee747cf4e361"),
        "runtime": UUID("df07ce66-fe48-4787-b210-087bb3b2a337"),
        "code_inputs.current_chat_history": UUID("b9fe0d7b-be2c-43fc-8c65-57300e40fb20"),
        "code_inputs.assistant_message": UUID("18dfa292-1cc8-4549-847e-152a5e7782df"),
    }
    output_display = {
        FinalAccumulationOfChatHistory.Outputs.result: NodeOutputDisplay(
            id=UUID("1c8268a2-4e31-4fd5-b493-0a9f28b7ec19"), name="result"
        ),
        FinalAccumulationOfChatHistory.Outputs.log: NodeOutputDisplay(
            id=UUID("a97f5cbf-3a00-4af7-921d-c553c8b3243f"), name="log"
        ),
    }
    port_displays = {
        FinalAccumulationOfChatHistory.Ports.default: PortDisplayOverrides(
            id=UUID("619a3089-4a05-4029-a248-cddb50facab7")
        )
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2820, y=825), width=466, height=315)
