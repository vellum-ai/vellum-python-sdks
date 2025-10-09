from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.output_linear_ticket import OutputLinearTicket


class OutputLinearTicketDisplay(BaseFinalOutputNodeDisplay[OutputLinearTicket]):
    label = "Output Linear Ticket"
    node_id = UUID("0a04a9e8-6b18-4fac-8a74-9bb16a8cf2f1")
    target_handle_id = UUID("6ecccece-249d-45d2-b26b-d9bf398708e6")
    output_name = "linear_ticket"
    node_input_ids_by_name = {"node_input": UUID("62653fbc-96da-45cd-8249-71b44505417a")}
    output_display = {
        OutputLinearTicket.Outputs.value: NodeOutputDisplay(
            id=UUID("79f7c63f-3378-4ab6-9355-d703036b24d4"), name="value"
        )
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3118, y=247),
        z_index=16,
        width=298,
        height=92,
        icon="vellum:icon:circle-stop",
        color="teal",
        comment=NodeDisplayComment(expanded=True, value="Returns the Linear ticket URL as workflow output."),
    )
