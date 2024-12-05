from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.prompt_node_19 import PromptNode19


class PromptNode19Display(BaseInlinePromptNodeDisplay[PromptNode19]):
    label = "Prompt Node 19"
    node_id = UUID("235b2e34-c6a3-48aa-b2cc-090571b41ea8")
    output_id = UUID("7b1ca9d1-d829-4329-b9f3-a864c3ce4230")
    array_output_id = UUID("17c0ef53-62bf-459f-8df8-2ff3f6b8852a")
    target_handle_id = UUID("35b77bfb-91d3-4e5b-8032-9786b9cc05c3")
    prompt_input_ids_by_name = {}
    node_input_ids_by_name = {}
    output_display = {
        PromptNode19.Outputs.text: NodeOutputDisplay(
            id=UUID("7b1ca9d1-d829-4329-b9f3-a864c3ce4230"), name="text"
        ),
        PromptNode19.Outputs.results: NodeOutputDisplay(
            id=UUID("17c0ef53-62bf-459f-8df8-2ff3f6b8852a"), name="results"
        ),
    }
    port_displays = {
        PromptNode19.Ports.default: PortDisplayOverrides(
            id=UUID("7b6c38d1-907d-4074-935e-b84a2a02786b")
        )
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3165.684879595973, y=768.6879108547903),
        width=480,
        height=170,
    )