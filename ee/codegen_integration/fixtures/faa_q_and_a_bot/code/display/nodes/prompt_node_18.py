from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.prompt_node_18 import PromptNode18


class PromptNode18Display(BaseInlinePromptNodeDisplay[PromptNode18]):
    label = "Prompt Node 18"
    node_id = UUID("9722b9da-0164-40fb-9270-a0fc9b87b1f9")
    output_id = UUID("df6d8990-e05b-45e1-9294-ccf58252757b")
    array_output_id = UUID("7bba9fdb-bb9e-457d-9755-a8f7ae0af959")
    target_handle_id = UUID("371cc948-bf59-4eba-9356-b21649f76b5e")
    node_input_ids_by_name = {"prompt_inputs.text": UUID("fbd03331-bbef-45f3-98fd-2106fd3cdb8a")}
    output_display = {
        PromptNode18.Outputs.text: NodeOutputDisplay(id=UUID("df6d8990-e05b-45e1-9294-ccf58252757b"), name="text"),
        PromptNode18.Outputs.results: NodeOutputDisplay(
            id=UUID("7bba9fdb-bb9e-457d-9755-a8f7ae0af959"), name="results"
        ),
        PromptNode18.Outputs.json: NodeOutputDisplay(id=UUID("23d497ef-7195-491d-8fc4-66858ee1cd37"), name="json"),
    }
    port_displays = {PromptNode18.Ports.default: PortDisplayOverrides(id=UUID("e80fd429-37ff-4054-9bd3-bd56568716e5"))}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=4524, y=946.5), width=480, height=168)
