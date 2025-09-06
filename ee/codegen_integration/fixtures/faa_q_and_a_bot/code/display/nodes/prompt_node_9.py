from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.prompt_node_9 import PromptNode9


class PromptNode9Display(BaseInlinePromptNodeDisplay[PromptNode9]):
    label = "Prompt Node 9"
    node_id = UUID("58e6c822-2d0d-4e81-9a00-0046a02741d4")
    output_id = UUID("e9c9ddb8-4057-4755-bbbd-6ca0291aac9a")
    array_output_id = UUID("3e174b5c-2e40-4bda-ba0c-eae3e617c988")
    target_handle_id = UUID("785dc582-83b3-46d1-87ec-9e8a10f4b00f")
    node_input_ids_by_name = {
        "prompt_inputs.question": UUID("c583f59e-2a5e-47c0-b244-2894b90d3d21"),
        "prompt_inputs.context": UUID("ded72461-3d6a-4633-a45e-e7cc9189941b"),
    }
    attribute_ids_by_name = {
        "ml_model": UUID("8ae0df7b-2d57-48d7-a396-37f3e3ef4c75"),
        "blocks": UUID("bd31dcbe-3a12-4bc1-948f-8fab8a2519ea"),
        "prompt_inputs": UUID("8036c42e-206f-4185-ad09-2f7abdddc125"),
        "functions": UUID("a3293819-18fa-45d7-9aa8-048d68e517e0"),
        "parameters": UUID("6d7092ef-35f8-46a3-babf-de70f22b86e4"),
    }
    output_display = {
        PromptNode9.Outputs.text: NodeOutputDisplay(id=UUID("e9c9ddb8-4057-4755-bbbd-6ca0291aac9a"), name="text"),
        PromptNode9.Outputs.results: NodeOutputDisplay(id=UUID("3e174b5c-2e40-4bda-ba0c-eae3e617c988"), name="results"),
        PromptNode9.Outputs.json: NodeOutputDisplay(id=UUID("91e77930-cd8e-48b2-983a-6ca7b41885a9"), name="json"),
    }
    port_displays = {PromptNode9.Ports.default: PortDisplayOverrides(id=UUID("ce8e3d37-4c41-4dce-aede-a343d2e1108a"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=4528.058075069296, y=-39.95100525832629), width=480, height=221
    )
