from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from .....nodes.parse_function_call.nodes.allowed_function_names import AllowedFunctionNames


class AllowedFunctionNamesDisplay(BaseTemplatingNodeDisplay[AllowedFunctionNames]):
    label = "Allowed Function Names"
    node_id = UUID("a5d4f0d5-747d-4469-8501-d8ee3165050e")
    target_handle_id = UUID("42ad9447-9fea-4e21-9ef8-dc5908e33ad9")
    node_input_ids_by_name = {"template": UUID("669d0c45-0f73-493e-85d9-bcc815419229")}
    output_display = {
        AllowedFunctionNames.Outputs.result: NodeOutputDisplay(
            id=UUID("c1f68169-345d-456d-afc6-0a5eb6db1f41"), name="result"
        )
    }
    port_displays = {
        AllowedFunctionNames.Ports.default: PortDisplayOverrides(id=UUID("1b86b935-cb3e-41ed-9477-e820e56c042c"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2910, y=1965), width=None, height=None)
