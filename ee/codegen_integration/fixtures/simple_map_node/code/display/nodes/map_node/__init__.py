from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseMapNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ....nodes.map_node import MapNode


class MapNodeDisplay(BaseMapNodeDisplay[MapNode]):
    label = "Map Node"
    node_id = UUID("72cb9f1e-aedd-47af-861e-4f38d27053b6")
    target_handle_id = UUID("0d15cb2c-256e-423e-a489-c9f87e181280")
    workflow_input_ids_by_name = {}
    node_input_ids_by_name = {"items": UUID("b8d66997-444e-4409-b315-5bef0c06192a")}
    port_displays = {MapNode.Ports.default: PortDisplayOverrides(id=UUID("239a1483-e4f5-4650-81a4-21c77d72cc5e"))}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=254, y=0), width=None, height=None)