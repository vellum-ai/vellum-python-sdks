from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("f0347fdc-1611-446c-b1da-408511d4181b")
    target_handle_id = UUID("f3ad283c-d092-4973-91e0-996e5859002a")
    output_id = UUID("b0961a8d-f702-4922-b410-2aecf7d34b68")
    output_name = "final-output"
    node_input_id = UUID("bb465fa1-defb-493c-8284-7156cd680fb3")
    node_input_ids_by_name = {"node_input": UUID("bb465fa1-defb-493c-8284-7156cd680fb3")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("b0961a8d-f702-4922-b410-2aecf7d34b68"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2752.5214681440443, y=210), width=478, height=234)
