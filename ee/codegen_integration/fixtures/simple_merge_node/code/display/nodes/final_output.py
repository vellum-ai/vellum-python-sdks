from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("7ea2c9ed-efb3-4d20-bf3d-7fafdaf6d842")
    target_handle_id = UUID("8a2df326-df6a-4a5e-81a3-12da082e468c")
    output_id = UUID("8988fa40-5083-4635-a647-bcbbf42c1652")
    output_name = "final-output"
    node_input_id = UUID("1cd60ba7-1bce-4ce0-b8b0-f2ab6bf9fc5c")
    node_input_ids_by_name = {"node_input": UUID("1cd60ba7-1bce-4ce0-b8b0-f2ab6bf9fc5c")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("8988fa40-5083-4635-a647-bcbbf42c1652"), name="value")
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3434.5298476454295, y=174.57146814404433), width=480, height=234
    )
