from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.add_evaluator_message_to_chat_history import AddEvaluatorMessageToChatHistory


class AddEvaluatorMessageToChatHistoryDisplay(BaseTemplatingNodeDisplay[AddEvaluatorMessageToChatHistory]):
    label = "Add Evaluator Message to Chat History"
    node_id = UUID("0ae79493-099c-49a6-9094-486bbccc2b97")
    target_handle_id = UUID("bc1575d8-1556-4052-a864-1e468e6e35b3")
    node_input_ids_by_name = {
        "inputs.chat_history": UUID("89044f30-ae4f-43f0-ad8d-609778fba156"),
        "template": UUID("bea2e9d8-7c94-4a43-abe2-caafaada1f88"),
        "inputs.message": UUID("797fbbd1-3fcb-4bab-a31c-796f09e71983"),
    }
    output_display = {
        AddEvaluatorMessageToChatHistory.Outputs.result: NodeOutputDisplay(
            id=UUID("5d2229df-6979-42a3-ae57-1e6c64e05a9d"), name="result"
        )
    }
    port_displays = {
        AddEvaluatorMessageToChatHistory.Ports.default: PortDisplayOverrides(
            id=UUID("6e2b0ca4-b44e-4ad1-9b27-47254e6d92b7")
        )
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3678.0195379564507, y=734.4758649232241), width=465, height=283
    )
