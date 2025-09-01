from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.templating_node import TemplatingNode


class TemplatingNodeDisplay(BaseTemplatingNodeDisplay[TemplatingNode]):
    label = "Templating Node"
    node_id = UUID("7dffcbb1-0a5c-4149-a6e9-f83095b0a871")
    target_handle_id = UUID("3522e32d-6735-499b-8d45-c0c6488ae92f")
    node_input_ids_by_name = {"template": UUID("5d2f0f48-4504-4979-8e24-92a8c08c23a4")}
    output_display = {
        TemplatingNode.Outputs.result: NodeOutputDisplay(id=UUID("4d39036a-fd6d-4a51-b410-7c0623375ebd"), name="result")
    }
    port_displays = {
        TemplatingNode.Ports.default: PortDisplayOverrides(id=UUID("9bce9d0a-3b0e-478e-8a97-f0510715a5a0"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2001.775709833795, y=296.65438885041556), width=480, height=224, z_index=None
    )
