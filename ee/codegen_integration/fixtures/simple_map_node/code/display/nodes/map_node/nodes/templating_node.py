from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from .....nodes.map_node.nodes.templating_node import TemplatingNode


class TemplatingNodeDisplay(BaseTemplatingNodeDisplay[TemplatingNode]):
    label = "Templating Node"
    node_id = UUID("24153572-e27b-4cea-a541-4d9e82f28b4e")
    target_handle_id = UUID("d1b8ef3d-1474-4cfb-8fb0-164f7b238a07")
    node_input_ids_by_name = {
        "inputs.example_var": UUID("5ec0a342-0d78-4717-bda3-e70805234cad"),
        "template": UUID("1cfb8efb-ac81-478a-ab46-46ed5536bd6f"),
        "inputs.var_1": UUID("73ff2e75-bebc-4f5a-970b-8ed733cc215c"),
    }
    output_display = {
        TemplatingNode.Outputs.result: NodeOutputDisplay(id=UUID("2e275abe-4e00-443b-9898-2afed7c13826"), name="result")
    }
    port_displays = {
        TemplatingNode.Ports.default: PortDisplayOverrides(id=UUID("401d5aee-afc0-4b7c-88a6-faaa753fd5c6"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1998.7584158889226, y=241.3446029681764), width=480, height=278
    )
