from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("4cf45b90-2ea9-4654-95a0-c00623766914")
    target_handle_id = UUID("973fc6ad-bf46-4f31-8544-04fcb4783cdd")
    output_id = UUID("e15f7fa4-cb16-4a38-8a8b-75ee6e77a95e")
    output_name = "final-output"
    node_input_id = UUID("215bb1c9-81d8-464a-a8bb-3f1812d8b4f3")
    node_input_ids_by_name = {"node_input": UUID("215bb1c9-81d8-464a-a8bb-3f1812d8b4f3")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("e15f7fa4-cb16-4a38-8a8b-75ee6e77a95e"), name="value")
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=5626.014123554148, y=1248.518870115668), width=460, height=239
    )
