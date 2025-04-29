from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.extract_by_chat_history import ExtractByChatHistory


class ExtractByChatHistoryDisplay(BaseInlinePromptNodeDisplay[ExtractByChatHistory]):
    label = "Extract by Chat History"
    node_id = UUID("b112e753-d690-4fe5-9d89-8e8addf570a0")
    output_id = UUID("a94cdd58-fef8-473a-bb00-ebf320a29fd4")
    array_output_id = UUID("1ff8bd8a-b927-49c1-bbf4-fcbbd9702d16")
    target_handle_id = UUID("f5f73970-2f63-4d5f-b379-b83d0f6afd72")
    node_input_ids_by_name = {"chat_history": UUID("7c67425d-da0a-4a0b-ae99-0284fa9ee92f")}
    output_display = {
        ExtractByChatHistory.Outputs.text: NodeOutputDisplay(
            id=UUID("a94cdd58-fef8-473a-bb00-ebf320a29fd4"), name="text"
        ),
        ExtractByChatHistory.Outputs.results: NodeOutputDisplay(
            id=UUID("1ff8bd8a-b927-49c1-bbf4-fcbbd9702d16"), name="results"
        ),
        ExtractByChatHistory.Outputs.json: NodeOutputDisplay(
            id=UUID("6815ce40-5016-4b54-b6e9-f60cdbf9645c"), name="json"
        ),
    }
    port_displays = {
        ExtractByChatHistory.Ports.default: PortDisplayOverrides(id=UUID("269f5117-6747-4a5f-b989-27fc9ceb0271"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=270.2777254920742, y=-23.060111113771768),
        width=480,
        height=279,
        comment=NodeDisplayComment(expanded=True),
    )
