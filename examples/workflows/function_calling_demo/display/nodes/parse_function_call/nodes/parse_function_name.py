from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from .....nodes.parse_function_call.nodes.parse_function_name import ParseFunctionName


class ParseFunctionNameDisplay(BaseTemplatingNodeDisplay[ParseFunctionName]):
    label = "Parse Function Name"
    node_id = UUID("14d5c7b2-e434-46a6-8b97-47450ea77dcd")
    target_handle_id = UUID("d2761e82-367e-4a10-b886-21413e52d9d5")
    node_input_ids_by_name = {
        "inputs.function_call": UUID("d15756f7-9021-469f-8e91-04f3008feaa3"),
        "template": UUID("4239a502-567a-4224-8f37-354883502192"),
    }
    output_display = {
        ParseFunctionName.Outputs.result: NodeOutputDisplay(
            id=UUID("063d66ff-547c-49c4-b62a-c0ca172f63c7"), name="result"
        )
    }
    port_displays = {
        ParseFunctionName.Ports.default: PortDisplayOverrides(id=UUID("5e7848c8-057e-404d-b00a-a4e198904bc2"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2955, y=630), width=None, height=None)
