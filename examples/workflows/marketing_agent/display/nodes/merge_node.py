from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseMergeNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides

from ...nodes.merge_node import MergeNode


class MergeNodeDisplay(BaseMergeNodeDisplay[MergeNode]):
    label = "Merge Node"
    node_id = UUID("e6af522a-f2d5-4766-b3aa-dfd4efab8ae7")
    target_handle_ids = [UUID("1129f497-602c-4edb-b413-934e003ba9a7"), UUID("ca0e9fe1-6ae6-43e0-847d-d4e577b61b4a")]
    port_displays = {MergeNode.Ports.default: PortDisplayOverrides(id=UUID("50cd16df-db58-4342-a3a2-5bfd2c8edd43"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2956.8514311076005, y=-890.613362433159), width=450, height=180
    )
