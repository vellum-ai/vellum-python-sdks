from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("4a6aadca-4d2f-40b8-a1a1-23db0f6a5767")
    target_handle_id = UUID("e5ef2f31-2199-4e1b-85d0-b5a79ab0595a")
    output_name = "final-output"
    node_input_ids_by_name = {"node_input": UUID("4ad8334f-b66b-49bd-828e-aef443bc3052")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("e869f551-b02c-465f-90b3-ad2021b3c618"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=3405, y=900), width=465, height=230)
