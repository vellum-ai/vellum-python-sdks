from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.prompt_node_19 import PromptNode19


class PromptNode19Display(BaseInlinePromptNodeDisplay[PromptNode19]):
    label = "Prompt Node 19"
    node_id = UUID("235b2e34-c6a3-48aa-b2cc-090571b41ea8")
    output_id = UUID("7b1ca9d1-d829-4329-b9f3-a864c3ce4230")
    array_output_id = UUID("17c0ef53-62bf-459f-8df8-2ff3f6b8852a")
    target_handle_id = UUID("35b77bfb-91d3-4e5b-8032-9786b9cc05c3")
    attribute_ids_by_name = {
        "ml_model": UUID("2010abdf-1f16-4979-96e4-c6bae7c4cd52"),
        "blocks": UUID("2d47190b-bba2-4546-88af-b2dc723365a1"),
        "prompt_inputs": UUID("091ee33c-abc5-461a-9d95-c15cccbcaf39"),
        "functions": UUID("f916eaa5-ac97-46f8-842c-ad2e65baf9ae"),
    }
    output_display = {
        PromptNode19.Outputs.text: NodeOutputDisplay(id=UUID("7b1ca9d1-d829-4329-b9f3-a864c3ce4230"), name="text"),
        PromptNode19.Outputs.results: NodeOutputDisplay(
            id=UUID("17c0ef53-62bf-459f-8df8-2ff3f6b8852a"), name="results"
        ),
        PromptNode19.Outputs.json: NodeOutputDisplay(id=UUID("57c13b8c-e07f-4608-afa1-9fe14e6a6359"), name="json"),
    }
    port_displays = {PromptNode19.Ports.default: PortDisplayOverrides(id=UUID("7b6c38d1-907d-4074-935e-b84a2a02786b"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3165.684879595973, y=768.6879108547903), width=480, height=170
    )
