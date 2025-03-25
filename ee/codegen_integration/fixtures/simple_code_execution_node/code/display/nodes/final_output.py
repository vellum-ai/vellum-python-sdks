from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("5bb10d67-efc7-4bd4-9452-4ec2ffbc031d")
    target_handle_id = UUID("ab9dd41a-5c7b-484a-bcd5-d55658ea849c")
    output_id = UUID("87760362-25b9-4dcb-8034-b49dc9e033ab")
    output_name = "final-output"
    node_input_id = UUID("d3b9060a-40b5-492c-a628-f2d3c912cf44")
    node_input_ids_by_name = {"node_input": UUID("d3b9060a-40b5-492c-a628-f2d3c912cf44")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("87760362-25b9-4dcb-8034-b49dc9e033ab"), name="value")
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2392.5396121883655, y=235.35180055401668), width=480, height=234
    )
