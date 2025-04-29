from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseMergeNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides

from ...nodes.merge_node import MergeNode


class MergeNodeDisplay(BaseMergeNodeDisplay[MergeNode]):
    label = "Merge Node"
    node_id = UUID("f67ad8f4-af4e-49c5-bc68-fb19c4c40e0d")
    target_handle_ids = [UUID("e734b04e-0965-4bde-b652-0ff94aae1230"), UUID("4a1f8760-f5f9-4b77-b062-3e1836db3e53")]
    node_input_ids_by_name = {}
    port_displays = {MergeNode.Ports.default: PortDisplayOverrides(id=UUID("7a906154-4a53-4406-b0c5-c7caabe1a8f1"))}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=4511.840798045603, y=1305), width=449, height=180)
