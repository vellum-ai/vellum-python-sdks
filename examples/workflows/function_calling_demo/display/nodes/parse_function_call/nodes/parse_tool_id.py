from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from .....nodes.parse_function_call.nodes.parse_tool_id import ParseToolID


class ParseToolIDDisplay(BaseTemplatingNodeDisplay[ParseToolID]):
    label = "Parse Tool ID"
    node_id = UUID("189de97f-9ae4-4af5-a816-0b54dbef616b")
    target_handle_id = UUID("0c3ad9b3-23cc-412a-a73e-b16622ab5cab")
    node_input_ids_by_name = {
        "inputs.function_call": UUID("b67b9af7-df91-4002-b501-aa8c7389f565"),
        "template": UUID("d8d8f969-ad9a-443c-9b15-0e53db265fa7"),
    }
    output_display = {
        ParseToolID.Outputs.result: NodeOutputDisplay(id=UUID("6df79e21-6e5d-45db-84e7-b16ec91f2302"), name="result")
    }
    port_displays = {ParseToolID.Ports.default: PortDisplayOverrides(id=UUID("3919adb3-bb78-4668-9dc1-22fca2c1e945"))}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2925, y=1500), width=None, height=None)
