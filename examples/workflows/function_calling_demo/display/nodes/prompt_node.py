from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.prompt_node import PromptNode


class PromptNodeDisplay(BaseInlinePromptNodeDisplay[PromptNode]):
    label = "Prompt Node"
    node_id = UUID("2f1fa0d5-ef23-4738-9fd5-216407c18fb1")
    output_id = UUID("76d8986c-3248-4a84-9780-97bd56b57cd7")
    array_output_id = UUID("044296d4-bfa5-43c5-9055-0d1d440cc05e")
    target_handle_id = UUID("b839c700-cbc7-442a-936a-a245a692df65")
    node_input_ids_by_name = {"prompt_inputs.chat_history": UUID("1cf292a8-a99b-460b-8348-392e4b3e8dee")}
    attribute_ids_by_name = {"ml_model": UUID("577cb543-4a7f-4f8a-8fce-56478c698511")}
    output_display = {
        PromptNode.Outputs.text: NodeOutputDisplay(id=UUID("76d8986c-3248-4a84-9780-97bd56b57cd7"), name="text"),
        PromptNode.Outputs.results: NodeOutputDisplay(id=UUID("044296d4-bfa5-43c5-9055-0d1d440cc05e"), name="results"),
        PromptNode.Outputs.json: NodeOutputDisplay(id=UUID("fdddc12a-b7ad-412e-b870-000567ec88a0"), name="json"),
    }
    port_displays = {PromptNode.Ports.default: PortDisplayOverrides(id=UUID("1aeebd8b-69c6-4051-af0e-01e628d81e3c"))}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=690, y=271.3250297289478), width=480, height=208)
