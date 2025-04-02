from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.prompt_node import PromptNode


class PromptNodeDisplay(BaseInlinePromptNodeDisplay[PromptNode]):
    label = "Prompt Node"
    node_id = UUID("393c798a-111a-4f73-bfee-5efb93228dcb")
    output_id = UUID("f7e45a43-f55c-4c19-8fe6-c3ce1308a076")
    array_output_id = UUID("63213d3c-547c-43df-905f-082aeb7dac61")
    target_handle_id = UUID("b14f0322-965d-43c9-96d4-7bce9fd87067")
    node_input_ids_by_name = {"prompt_inputs.var_1": UUID("183b03e5-b903-4d39-abe4-9267c78285f6")}
    output_display = {
        PromptNode.Outputs.text: NodeOutputDisplay(id=UUID("f7e45a43-f55c-4c19-8fe6-c3ce1308a076"), name="text"),
        PromptNode.Outputs.results: NodeOutputDisplay(id=UUID("63213d3c-547c-43df-905f-082aeb7dac61"), name="results"),
        PromptNode.Outputs.json: NodeOutputDisplay(id=UUID("981a3c2e-f173-40d0-9ef0-663d7f1038a1"), name="json"),
    }
    port_displays = {PromptNode.Ports.default: PortDisplayOverrides(id=UUID("f743c0c0-8ced-445d-bf1c-bef1f2b26895"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=866.1444593268898, y=545.562737655267), width=480, height=168
    )
