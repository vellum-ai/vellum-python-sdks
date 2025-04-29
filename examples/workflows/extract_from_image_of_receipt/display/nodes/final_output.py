from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("25746d6b-3749-401e-9111-00a64737949c")
    target_handle_id = UUID("6ff6d0f8-c629-42e7-bbf1-272028c2979e")
    output_name = "final-output"
    node_input_ids_by_name = {"node_input": UUID("d5983b77-b8f4-4d3c-9aa1-c83830e5a919")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("dfa69d72-3f2a-4f56-b639-5f0331ed5dc5"), name="value")
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1619.1089509093895, y=-195.73728608411776), width=522, height=400
    )
