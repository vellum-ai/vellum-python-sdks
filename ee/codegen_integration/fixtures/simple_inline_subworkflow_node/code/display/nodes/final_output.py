from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("075932b7-c6ba-4c3a-8c8f-d6b043f8fe48")
    target_handle_id = UUID("abf4fec7-4053-417c-bf17-21819155d4d1")
    output_id = UUID("b38e08c7-904d-4f49-b8fb-56e1eff254d6")
    output_name = "final-output"
    node_input_id = UUID("e4585fda-2016-40fb-8ceb-6553a73f0311")
    node_input_ids_by_name = {"node_input": UUID("e4585fda-2016-40fb-8ceb-6553a73f0311")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("b38e08c7-904d-4f49-b8fb-56e1eff254d6"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2750, y=210), width=480, height=233)
