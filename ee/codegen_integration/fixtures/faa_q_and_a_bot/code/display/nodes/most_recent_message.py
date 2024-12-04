from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.most_recent_message import MostRecentMessage


class MostRecentMessageDisplay(BaseTemplatingNodeDisplay[MostRecentMessage]):
    label = "Most Recent Message"
    node_id = UUID("e1aa5d7e-8e6e-471b-ad21-93fdb350d04c")
    output_id = UUID("6239dc48-5fbc-44bc-b99d-5833d6a386bd")
    target_handle_id = UUID("157d01bd-441e-49fa-abce-7b991c9291da")
    template_input_id = UUID("b6f8e86f-93ba-4200-9097-421723348d3d")
    node_input_ids_by_name = {
        "chat_history": UUID("fec02d64-f82c-4970-bd57-31c84aaf7214"),
        "template": UUID("b6f8e86f-93ba-4200-9097-421723348d3d"),
    }
    port_displays = {
        MostRecentMessage.Ports.default: PortDisplayOverrides(
            id=UUID("ab8e97b4-4ee4-42bc-8f43-e2c9c457ad21")
        )
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=254, y=237.3190436953056), width=480, height=221
    )
