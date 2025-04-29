from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseMergeNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides

from .....nodes.parse_function_call.nodes.merge_node import MergeNode


class MergeNodeDisplay(BaseMergeNodeDisplay[MergeNode]):
    label = "Merge Node"
    node_id = UUID("bafc16db-a476-436d-9dde-fb74e8c294a0")
    target_handle_ids = [
        UUID("d3539134-8ba5-461f-b96c-8dda2b2bcc18"),
        UUID("9dd8f0b4-dc15-456b-af35-68ca7c0ab1d7"),
        UUID("a783d560-204c-45de-b8eb-ede63936ddaf"),
        UUID("0d6fd7aa-1ca0-4246-8920-e1f00272ca78"),
    ]
    port_displays = {MergeNode.Ports.default: PortDisplayOverrides(id=UUID("c3beb021-47d9-44b1-bd2b-81b11168e76d"))}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=3480, y=1005), width=None, height=None)
