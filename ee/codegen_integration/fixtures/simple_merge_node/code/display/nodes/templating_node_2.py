from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.templating_node_2 import TemplatingNode2


class TemplatingNode2Display(BaseTemplatingNodeDisplay[TemplatingNode2]):
    label = "Templating Node"
    node_id = UUID("5b7d7b3f-e10d-4334-a217-9099dececd8d")
    target_handle_id = UUID("f9a55e22-2cbd-4492-8755-36760320f0d9")
    node_input_ids_by_name = {"template": UUID("6567617f-57e4-4c11-9175-557108fcf07e")}
    output_display = {
        TemplatingNode2.Outputs.result: NodeOutputDisplay(
            id=UUID("b96fcdbd-7bd1-4cd1-b91a-49bb50ded865"), name="result"
        )
    }
    port_displays = {
        TemplatingNode2.Ports.default: PortDisplayOverrides(id=UUID("a5ae5a5c-ad8a-4a19-a726-f3b8ed1fbb1b"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1827.1240707957352, y=438.20962675410783),
        width=480,
        height=224,
        icon="vellum:icon:stamp",
        color="brown",
    )
