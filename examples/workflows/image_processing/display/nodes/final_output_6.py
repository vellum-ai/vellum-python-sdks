from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.final_output_6 import FinalOutput6


class FinalOutput6Display(BaseFinalOutputNodeDisplay[FinalOutput6]):
    label = "Final Output 6"
    node_id = UUID("4e5f53c8-9ae6-47c4-9263-7ba72997e144")
    target_handle_id = UUID("b59692d5-f479-45ce-b745-437ddfd11397")
    output_name = "final-output-6"
    node_input_ids_by_name = {"node_input": UUID("d453e26e-8794-4a80-afd8-4cdfa4d2f91f")}
    output_display = {
        FinalOutput6.Outputs.value: NodeOutputDisplay(id=UUID("92f6b627-7e91-49d1-9f26-4fb139a7f9a9"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=864, y=16.5), width=456, height=239)
