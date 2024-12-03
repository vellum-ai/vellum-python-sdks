from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("ed688426-1976-4d0c-9f3a-2a0b0fae161a")
    target_handle_id = UUID("b28439f6-0c1e-44c0-87b1-b7fa3c7408b2")
    output_id = UUID("43e128f4-24fe-4484-9d08-948a4a390707")
    output_name = "final-output"
    node_input_id = UUID("097798e5-9330-46a4-b8ec-e93532668d37")
    node_input_ids_by_name = {"node_input": UUID("097798e5-9330-46a4-b8ec-e93532668d37")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("43e128f4-24fe-4484-9d08-948a4a390707"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2750, y=210), width=480, height=234)
