from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.templating_node_1 import TemplatingNode1


class TemplatingNode1Display(BaseTemplatingNodeDisplay[TemplatingNode1]):
    label = "Templating Node"
    node_id = UUID("6c5017d1-9aa3-4f34-9a6a-fbe2f7029473")
    target_handle_id = UUID("2d2c5559-983f-469c-a1d0-c2fe9f8f3639")
    node_input_ids_by_name = {"template": UUID("3981811f-6e33-48b6-b7c5-c32ba9a97dc8")}
    output_display = {
        TemplatingNode1.Outputs.result: NodeOutputDisplay(
            id=UUID("6a903b23-d66c-413b-996d-109f6a483056"), name="result"
        )
    }
    port_displays = {
        TemplatingNode1.Ports.default: PortDisplayOverrides(id=UUID("e900aa36-b59e-4d13-bb66-21967eb02214"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1824.7678784335756, y=-124.21640253267435), width=480, height=224
    )
