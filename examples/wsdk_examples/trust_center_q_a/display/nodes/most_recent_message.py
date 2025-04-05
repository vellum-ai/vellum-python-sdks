from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.most_recent_message import MostRecentMessage


class MostRecentMessageDisplay(BaseTemplatingNodeDisplay[MostRecentMessage]):
    label = "Most Recent Message"
    node_id = UUID("4f33effa-a71a-4850-8340-d1d271ec84ae")
    target_handle_id = UUID("23ec9395-1369-4af8-a4ae-097acc4dbd58")
    node_input_ids_by_name = {
        "inputs.chat_history": UUID("31f0848f-58bc-48ff-8032-ea038e27e7db"),
        "template": UUID("8a01c440-8061-46ae-b884-841ac1ce62b0"),
    }
    output_display = {
        MostRecentMessage.Outputs.result: NodeOutputDisplay(
            id=UUID("b233ca47-3ab5-41b9-9355-605b830bfb22"), name="result"
        )
    }
    port_displays = {
        MostRecentMessage.Ports.default: PortDisplayOverrides(id=UUID("823834a2-0968-4d33-8baf-e23445a15c7f"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1785, y=225), width=448, height=315, comment=NodeDisplayComment(expanded=True)
    )
