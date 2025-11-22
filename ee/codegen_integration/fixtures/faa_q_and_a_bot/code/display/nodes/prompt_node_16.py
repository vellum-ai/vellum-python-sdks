from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.prompt_node_16 import PromptNode16


class PromptNode16Display(BaseInlinePromptNodeDisplay[PromptNode16]):
    label = "Prompt Node 16"
    node_id = UUID("4e377068-94d3-4215-8366-261b7541ef37")
    output_id = UUID("4d31e604-6711-4a12-b618-476bfc304f09")
    array_output_id = UUID("4dba2219-6714-4ca7-9076-5bb01ee0b340")
    target_handle_id = UUID("ba029d72-7fc2-4e82-a5ad-6f364c84d72f")
    node_input_ids_by_name = {"prompt_inputs.most_recent_message": UUID("0f0f394c-dc7d-46a1-9217-24c1e59b273a")}
    attribute_ids_by_name = {
        "ml_model": UUID("35c7463b-4fb3-44aa-8c2b-1f30ab4b71ac"),
        "blocks": UUID("805ae978-3d9f-4d39-a433-d7812542c532"),
        "prompt_inputs": UUID("35ae3ecc-030b-479d-b6c8-c2ccdd7ae984"),
        "functions": UUID("e9e50650-027f-4595-9479-b4e488153402"),
        "parameters": UUID("fb2b621f-f975-4e58-ad3b-d074c2a03d3d"),
    }
    output_display = {
        PromptNode16.Outputs.text: NodeOutputDisplay(id=UUID("4d31e604-6711-4a12-b618-476bfc304f09"), name="text"),
        PromptNode16.Outputs.results: NodeOutputDisplay(
            id=UUID("4dba2219-6714-4ca7-9076-5bb01ee0b340"), name="results"
        ),
        PromptNode16.Outputs.json: NodeOutputDisplay(id=UUID("7ef91456-d48e-4c5e-8ba6-a608f36584c5"), name="json"),
    }
    port_displays = {PromptNode16.Ports.default: PortDisplayOverrides(id=UUID("aa013fc4-618d-4cf4-88ce-639c56588aa3"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2694, y=1100), width=480, height=168, icon="vellum:icon:text-size", color="navy"
    )
