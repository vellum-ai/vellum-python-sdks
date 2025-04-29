from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("5fb0cb00-8b8d-48c9-b428-077c08ada4b6")
    target_handle_id = UUID("7ed44929-f24c-4c81-bc98-932383b04ab6")
    output_name = "final-output"
    node_input_ids_by_name = {"node_input": UUID("7190d0e3-47c1-4fee-97b8-a56b75585afa")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("d864d797-940c-44c1-a59d-a014ce5b9551"), name="value")
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=4351.825508233975, y=269.66595271050653), width=462, height=239
    )
