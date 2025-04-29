from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from .....nodes.parse_function_call.nodes.parse_function_args import ParseFunctionArgs


class ParseFunctionArgsDisplay(BaseTemplatingNodeDisplay[ParseFunctionArgs]):
    label = "Parse Function Args"
    node_id = UUID("8578e405-2e94-4603-88b2-f6420af5135b")
    target_handle_id = UUID("8d4f5e8c-3124-4049-89d5-1261f6838400")
    node_input_ids_by_name = {
        "inputs.function_call": UUID("5b3a91bc-4375-45a1-9fa7-c61f52484678"),
        "template": UUID("09cae3d9-6444-4352-9d04-532a0b703303"),
    }
    output_display = {
        ParseFunctionArgs.Outputs.result: NodeOutputDisplay(
            id=UUID("aa9c4408-4251-4a48-9b8f-882912966dec"), name="result"
        )
    }
    port_displays = {
        ParseFunctionArgs.Ports.default: PortDisplayOverrides(id=UUID("553960a1-8c83-4da5-9484-cf96c625cd9d"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2925, y=1035), width=None, height=None)
