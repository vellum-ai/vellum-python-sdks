from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("08cf5b7e-2668-4f27-95c5-f28236d5be47")
    target_handle_id = UUID("a09307c3-78f6-4aca-bbc0-e8ec24fc2a64")
    output_name = "final-output"
    node_input_ids_by_name = {"node_input": UUID("c84aa0bd-3440-4507-bae4-586dae3b9f22")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("9c3830c9-7faa-4872-83e5-7360f662f8e2"), name="value")
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1465.3578490588761, y=635.1421509411235), width=521, height=448
    )
