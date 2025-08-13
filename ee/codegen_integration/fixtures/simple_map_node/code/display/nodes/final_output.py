from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("fa0d5829-f259-4db8-a11a-b12fd7237ea5")
    target_handle_id = UUID("8e19172a-4f87-4c21-8c91-ccdfb3e74c16")
    output_name = "final-output"
    node_input_ids_by_name = {"node_input": UUID("ca8f8a34-24d3-4941-893f-73c5e3bbb66c")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("d9269719-a7a2-4388-9b85-73e329a78d16"), name="value")
    }
    port_displays = {FinalOutput.Ports.default: PortDisplayOverrides(id=UUID("c42bd1b2-6a2d-40ef-8f58-47ab6f145774"))}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=864, y=58.5), width=454, height=234)
