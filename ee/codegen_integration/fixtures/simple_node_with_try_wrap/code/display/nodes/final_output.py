from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("54803ff7-9afd-4eb1-bff3-242345d3443d")
    target_handle_id = UUID("6bf50c29-d2f5-4a4f-a63b-907c9053833d")
    output_name = "final-output"
    node_input_ids_by_name = {"node_input": UUID("960ac634-0081-4e20-9ab8-c98b826fbfc6")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("f1eca494-a7dc-41c0-9c74-9658a64955e6"), name="value")
    }
    port_displays = {FinalOutput.Ports.default: PortDisplayOverrides(id=UUID("864fab2d-1313-4290-94d1-51dcf3511d40"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2761.0242006615217, y=208.9757993384785), width=474, height=234
    )
