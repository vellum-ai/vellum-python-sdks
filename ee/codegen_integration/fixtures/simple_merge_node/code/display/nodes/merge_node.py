from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseMergeNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides

from ...nodes.merge_node import MergeNode


class MergeNodeDisplay(BaseMergeNodeDisplay[MergeNode]):
    node_id = UUID("7426f273-a43d-4448-a2d2-76d0ee0d069c")
    target_handle_ids = [UUID("dee0633e-0221-40c7-b179-aae1cf67de87"), UUID("cf6974a6-1676-43ed-99a0-66bd3eac235f")]
    port_displays = {MergeNode.Ports.default: PortDisplayOverrides(id=UUID("e0e666c4-a90b-4a95-928e-144bab251356"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2374.2549861495845, y=205.20096952908594), width=476, height=180
    )
