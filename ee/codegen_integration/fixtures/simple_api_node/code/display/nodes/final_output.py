from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("dad01b99-c0b4-4904-a75e-066fa947d256")
    target_handle_id = UUID("2d005e2b-e8bb-404a-9702-8faf10c2213d")
    output_id = UUID("e53bdfb1-f74d-43f0-a3fc-24c7a5162a62")
    output_name = "final-output"
    node_input_id = UUID("bc3e4cad-e6b6-4f3d-b0d8-ee7099fe6352")
    node_input_ids_by_name = {"node_input": UUID("bc3e4cad-e6b6-4f3d-b0d8-ee7099fe6352")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("e53bdfb1-f74d-43f0-a3fc-24c7a5162a62"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2750, y=210), width=467, height=234)
