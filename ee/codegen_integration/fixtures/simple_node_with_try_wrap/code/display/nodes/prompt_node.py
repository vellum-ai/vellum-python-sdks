from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay, BaseTryNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.prompt_node import PromptNode


@BaseTryNodeDisplay.wrap(node_id=UUID("42823c15-2ba6-4c85-a0d7-74a4e0541a42"))
class PromptNodeDisplay(BaseInlinePromptNodeDisplay[PromptNode]):
    label = "Prompt"
    node_id = UUID("1645c7e7-1b5f-4ca3-9610-0c5ac30a77ff")
    output_id = UUID("13e677d3-14e7-4b0c-ab36-834bb99c930c")
    array_output_id = UUID("01976625-90e7-4ecb-b752-454b2cd0bb67")
    target_handle_id = UUID("e31c38be-ef5a-4c20-ab8b-9315f3e75ff8")
    node_input_ids_by_name = {"prompt_inputs.text": UUID("b2bc9402-6e50-4982-800c-1662c188899b")}
    attribute_ids_by_name = {
        "ml_model": UUID("38f60afe-cd5f-4950-8674-18e17567a784"),
        "prompt_inputs": UUID("91448235-24d7-4ee1-bba4-3bbce03ebdcb"),
        "functions": UUID("6052c618-675a-4e6b-9276-498ab97deba7"),
    }
    output_display = {
        PromptNode.Outputs.text: NodeOutputDisplay(id=UUID("13e677d3-14e7-4b0c-ab36-834bb99c930c"), name="text"),
        PromptNode.Outputs.results: NodeOutputDisplay(id=UUID("01976625-90e7-4ecb-b752-454b2cd0bb67"), name="results"),
        PromptNode.Outputs.json: NodeOutputDisplay(id=UUID("6f89f74a-32d8-43a5-8414-fdd7ae9265b4"), name="json"),
    }
    port_displays = {PromptNode.Ports.default: PortDisplayOverrides(id=UUID("4e8bdb06-2adb-474f-9bd7-f6ee01fd4c2b"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2083.6598676957, y=288.95993689582167), width=480, height=126
    )
