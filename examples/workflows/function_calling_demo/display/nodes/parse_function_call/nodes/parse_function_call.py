from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from .....nodes.parse_function_call.nodes.parse_function_call import ParseFunctionCall1


class ParseFunctionCall1Display(BaseTemplatingNodeDisplay[ParseFunctionCall1]):
    label = "Parse Function Call"
    node_id = UUID("40f2e0f6-9d30-4c94-a09d-d88be7c871d6")
    target_handle_id = UUID("f3ae9773-9729-4ae9-a608-3cc2a5a0ade8")
    node_input_ids_by_name = {
        "inputs.output": UUID("69e35fe1-9920-450c-b524-757d5900f810"),
        "template": UUID("ddf266be-2166-404c-986f-631cffa05fbc"),
    }
    output_display = {
        ParseFunctionCall1.Outputs.result: NodeOutputDisplay(
            id=UUID("a165e831-0c3d-414e-85a0-f17d53166759"), name="result"
        )
    }
    port_displays = {
        ParseFunctionCall1.Ports.default: PortDisplayOverrides(id=UUID("4a5084ce-5c40-4af7-917f-e412e86f21e6"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=1725, y=495), width=None, height=None)
