from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.prompt_node import PromptNode


class PromptNodeDisplay(BaseInlinePromptNodeDisplay[PromptNode]):
    label = "Prompt Node"
    node_id = UUID("7e09927b-6d6f-4829-92c9-54e66bdcaf80")
    output_id = UUID("2d4f1826-de75-499a-8f84-0a690c8136ad")
    array_output_id = UUID("771c6fba-5b4a-4092-9d52-693242d7b92c")
    target_handle_id = UUID("3feb7e71-ec63-4d58-82ba-c3df829a2948")
    node_input_ids_by_name = {"prompt_inputs.text": UUID("7b8af68b-cf60-4fca-9c57-868042b5b616")}
    attribute_ids_by_name = {
        "ml_model": UUID("bb466968-7547-458c-8e8f-5d0fb1eb33f5"),
        "blocks": UUID("6a3ab4d8-4ff6-43fe-a919-93b2a05fa0a6"),
        "prompt_inputs": UUID("84bafdbf-3ca8-4e48-9ea6-380e90756a7f"),
        "parameters": UUID("56de8c71-1f6c-4a0d-b566-f6b27265b71a"),
        "functions": UUID("2a8be1e2-2dad-4a2f-80be-01c4723ce1da"),
    }
    output_display = {
        PromptNode.Outputs.text: NodeOutputDisplay(id=UUID("2d4f1826-de75-499a-8f84-0a690c8136ad"), name="text"),
        PromptNode.Outputs.results: NodeOutputDisplay(id=UUID("771c6fba-5b4a-4092-9d52-693242d7b92c"), name="results"),
        PromptNode.Outputs.json: NodeOutputDisplay(id=UUID("6f89f74a-32d8-43a5-8414-fdd7ae9265b4"), name="json"),
    }
    port_displays = {PromptNode.Ports.default: PortDisplayOverrides(id=UUID("dd8397b1-5a41-4fa0-8c24-e5dffee4fb98"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2083.6598676957, y=288.95993689582167), width=480, height=126, z_index=None
    )
