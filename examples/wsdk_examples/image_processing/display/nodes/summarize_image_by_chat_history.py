from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.summarize_image_by_chat_history import SummarizeImageByChatHistory


class SummarizeImageByChatHistoryDisplay(BaseInlinePromptNodeDisplay[SummarizeImageByChatHistory]):
    label = "Summarize Image by Chat History"
    node_id = UUID("dca4c915-ffe8-455b-8dec-7295e38f5387")
    output_id = UUID("1d8e3718-2de2-414c-a63d-4d7a619bea2c")
    array_output_id = UUID("fbe26292-6e59-430b-b21a-f27b21fb6b1b")
    target_handle_id = UUID("90d5b58b-c00c-4461-9ab6-1a10c40f3e2b")
    node_input_ids_by_name = {"chat_history": UUID("79d83f9e-fb6f-451f-95f1-ff21c2cb1801")}
    output_display = {
        SummarizeImageByChatHistory.Outputs.text: NodeOutputDisplay(
            id=UUID("1d8e3718-2de2-414c-a63d-4d7a619bea2c"), name="text"
        ),
        SummarizeImageByChatHistory.Outputs.results: NodeOutputDisplay(
            id=UUID("fbe26292-6e59-430b-b21a-f27b21fb6b1b"), name="results"
        ),
        SummarizeImageByChatHistory.Outputs.json: NodeOutputDisplay(
            id=UUID("feec03e7-eed8-4399-8b02-72be44af5653"), name="json"
        ),
    }
    port_displays = {
        SummarizeImageByChatHistory.Ports.default: PortDisplayOverrides(id=UUID("1c874657-aa34-4aa5-91cb-a8cdfbf7347a"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=270.2777254920742, y=-23.060111113771768),
        width=480,
        height=279,
        comment=NodeDisplayComment(expanded=True),
    )
