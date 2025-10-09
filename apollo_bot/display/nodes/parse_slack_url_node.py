from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.parse_slack_url_node import ParseSlackUrlNode


class ParseSlackUrlNodeDisplay(BaseNodeDisplay[ParseSlackUrlNode]):
    label = "ParseSlackUrlNode"
    node_id = UUID("6121937f-69ff-427d-ae42-941f646dae0e")
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=610, y=0), z_index=9, icon="vellum:icon:square", color="peach"
    )
    attribute_ids_by_name = {"slack_url": UUID("ce5b6b73-c7c5-42e6-84c8-7e51f2392b4b")}
    output_display = {
        ParseSlackUrlNode.Outputs.channel_id: NodeOutputDisplay(
            id=UUID("7d0f82fe-8465-4d49-afda-73aee3628bcd"), name="channel_id"
        ),
        ParseSlackUrlNode.Outputs.message_ts: NodeOutputDisplay(
            id=UUID("23281dc5-d3ec-446b-86b5-40a10433953d"), name="message_ts"
        ),
    }
    port_displays = {
        ParseSlackUrlNode.Ports.default: PortDisplayOverrides(id=UUID("6eafabf4-0e20-4775-b07c-8e9ed6474b69"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=610, y=0), z_index=9, icon="vellum:icon:square", color="peach"
    )
