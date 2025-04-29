from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.my_prompt import MyPrompt


class MyPromptDisplay(BaseInlinePromptNodeDisplay[MyPrompt]):
    label = "My Prompt"
    node_id = UUID("805fa2c2-56fb-400d-9ca2-486c753bc81d")
    output_id = UUID("2bae09e7-f310-446d-9471-563446262d4b")
    array_output_id = UUID("7a1fd6fd-070e-417a-919b-52520f0429e2")
    target_handle_id = UUID("7e899794-657a-412f-b72d-8e7e4b151a01")
    node_input_ids_by_name = {"prompt_inputs.query": UUID("ebae7e5c-c916-4c07-be2c-40929eed766b")}
    output_display = {
        MyPrompt.Outputs.text: NodeOutputDisplay(id=UUID("2bae09e7-f310-446d-9471-563446262d4b"), name="text"),
        MyPrompt.Outputs.results: NodeOutputDisplay(id=UUID("7a1fd6fd-070e-417a-919b-52520f0429e2"), name="results"),
        MyPrompt.Outputs.json: NodeOutputDisplay(id=UUID("9498ab4d-f0a2-4666-b3eb-59284fe11583"), name="json"),
    }
    port_displays = {MyPrompt.Ports.default: PortDisplayOverrides(id=UUID("20d70a2d-01c5-4c98-9fa2-2c1b200d492f"))}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=None, height=None)
