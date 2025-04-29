from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.output_type import OutputType


class OutputTypeDisplay(BaseTemplatingNodeDisplay[OutputType]):
    label = "Output Type"
    node_id = UUID("122e6aed-eee1-448c-8fb0-9746aa3c63f4")
    target_handle_id = UUID("7bad755b-7f00-4c5f-a66d-4e099902cb4f")
    node_input_ids_by_name = {
        "inputs.output": UUID("76a43566-ea34-4547-bded-0f77652671ae"),
        "template": UUID("15e4e329-b479-4b66-a105-2420c8796970"),
    }
    output_display = {
        OutputType.Outputs.result: NodeOutputDisplay(id=UUID("7d17e99d-3929-4672-9fbd-ad7eb5cae0d2"), name="result")
    }
    port_displays = {OutputType.Ports.default: PortDisplayOverrides(id=UUID("457cd3cf-893d-421d-a4f0-47872d7df7ac"))}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=1485, y=285), width=453, height=221)
