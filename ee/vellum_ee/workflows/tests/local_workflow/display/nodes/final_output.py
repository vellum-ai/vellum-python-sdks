from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("f3ef4b2b-fec9-4026-9cc6-e5eac295307f")
    target_handle_id = UUID("3ec34f6e-da48-40d5-a65b-a48fefa75763")
    output_id = UUID("5469b810-6ea6-4362-9e79-e360d44a1405")
    output_name = "final-output"
    node_input_id = UUID("fe6cba85-2423-4b5e-8f85-06311a8be5fb")
    node_input_ids_by_name = {"node_input": UUID("fe6cba85-2423-4b5e-8f85-06311a8be5fb")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("5469b810-6ea6-4362-9e79-e360d44a1405"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2750, y=210), width=459, height=234)
