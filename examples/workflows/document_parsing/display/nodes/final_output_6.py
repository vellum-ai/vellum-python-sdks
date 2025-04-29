from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.final_output_6 import FinalOutput6


class FinalOutput6Display(BaseFinalOutputNodeDisplay[FinalOutput6]):
    label = "Final Output 6"
    node_id = UUID("941add93-b7aa-469a-9c25-740fe80009a5")
    target_handle_id = UUID("4e8d14bf-1dfc-4afa-8863-5bf951559308")
    output_name = "final-output-6"
    node_input_ids_by_name = {"node_input": UUID("0a6972dc-ac3a-4d99-9577-be4c4c3dc2a7")}
    output_display = {
        FinalOutput6.Outputs.value: NodeOutputDisplay(id=UUID("4dfe9122-354b-4796-a2de-4eaa38a0c5df"), name="value")
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=969.5727079556486, y=-167.19651184282836), width=521, height=507
    )
