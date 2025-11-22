from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.templating_node import TemplatingNode


class TemplatingNodeDisplay(BaseTemplatingNodeDisplay[TemplatingNode]):
    label = "Templating Node"
    node_id = UUID("d0538e54-b623-4a71-a5cd-24b1ed5ce223")
    target_handle_id = UUID("62e924f8-3f80-475f-b6f0-bda3420a50bc")
    node_input_ids_by_name = {
        "inputs.example_var_1": UUID("5e8396fe-1803-405f-ab1b-95132b592552"),
        "template": UUID("e7904d49-cb35-4bc8-8dd6-3c8e243353d2"),
    }
    output_display = {
        TemplatingNode.Outputs.result: NodeOutputDisplay(id=UUID("c66c362b-bb83-4333-a691-b72dc9a8734d"), name="result")
    }
    port_displays = {
        TemplatingNode.Ports.default: PortDisplayOverrides(id=UUID("74e0d264-fed6-453f-8769-23f26b976fc2"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1934.0008032128517, y=219.2219534344094),
        width=466,
        height=224,
        icon="vellum:icon:stamp",
        color="brown",
    )
