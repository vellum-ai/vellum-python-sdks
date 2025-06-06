from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.prompt_node_14 import PromptNode14


class PromptNode14Display(BaseInlinePromptNodeDisplay[PromptNode14]):
    label = "Prompt Node 14"
    node_id = UUID("3f4ce7b7-8389-42e1-abab-a7afe9a142b5")
    output_id = UUID("8e2d57c3-85a3-4acb-b4d3-998c6906e389")
    array_output_id = UUID("43cd2bcf-4c99-4f7a-ace7-e27d986dd041")
    target_handle_id = UUID("3485b3fb-e4ee-47c9-b567-c5eab60c01f9")
    node_input_ids_by_name = {"prompt_inputs.chat_history": UUID("b6524b5f-7697-4923-8b87-f85baadb505a")}
    attribute_ids_by_name = {
        "ml_model": UUID("4c6baea4-e4c9-4ea2-bffd-88d0b7210725"),
        "prompt_inputs": UUID("5736796a-5529-4cbe-a930-9b2067e21aca"),
        "functions": UUID("1a360feb-6271-4b9c-a543-6ff1af06391d"),
    }
    output_display = {
        PromptNode14.Outputs.text: NodeOutputDisplay(id=UUID("8e2d57c3-85a3-4acb-b4d3-998c6906e389"), name="text"),
        PromptNode14.Outputs.results: NodeOutputDisplay(
            id=UUID("43cd2bcf-4c99-4f7a-ace7-e27d986dd041"), name="results"
        ),
        PromptNode14.Outputs.json: NodeOutputDisplay(id=UUID("3c742327-c345-4b45-b829-778fd84de9c4"), name="json"),
    }
    port_displays = {PromptNode14.Ports.default: PortDisplayOverrides(id=UUID("23556dd8-b9f8-4cf7-9c24-291f9d0a223a"))}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=4524, y=631), width=480, height=168)
