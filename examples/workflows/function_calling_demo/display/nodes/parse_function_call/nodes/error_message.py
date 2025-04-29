from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from .....nodes.parse_function_call.nodes.error_message import ErrorMessage


class ErrorMessageDisplay(BaseTemplatingNodeDisplay[ErrorMessage]):
    label = "Error Message"
    node_id = UUID("d5c71b95-8f26-46b9-b0ba-25ba723b7886")
    target_handle_id = UUID("db91f735-b082-4762-8125-63880c5e380d")
    node_input_ids_by_name = {
        "inputs.invalid_function_name": UUID("f34229bf-1912-451c-8d4e-cf8d061ddf32"),
        "template": UUID("438b35a2-5163-4978-af95-fb85e2023035"),
    }
    output_display = {
        ErrorMessage.Outputs.result: NodeOutputDisplay(id=UUID("b777ddb5-87c7-4939-8cc8-7ee31d322d5a"), name="result")
    }
    port_displays = {ErrorMessage.Ports.default: PortDisplayOverrides(id=UUID("e985f530-f306-4ab9-9b8b-ca54c64a4b81"))}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=5355, y=1275), width=None, height=None)
