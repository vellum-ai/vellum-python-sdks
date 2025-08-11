from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("e99362a0-3fe5-4703-ba40-6125bf028bfd")
    target_handle_id = UUID("f3f899c5-0125-46ca-95e7-d34eee06d7e6")
    output_name = "final-output"
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("53a3b97c-461e-4441-a513-36a8545a20cd"), name="value")
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2512.1922540269998, y=121.74320933615763), width=522, height=602
    )
