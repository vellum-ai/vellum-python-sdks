from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseErrorNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.error_node import ErrorNode


class ErrorNodeDisplay(BaseErrorNodeDisplay[ErrorNode]):
    label = "Error Node"
    node_input_ids_by_name = {"error_source_input_id": UUID("f3a0d8b9-7772-4db6-8e28-f49f8c4d9e2a")}
    port_displays = {ErrorNode.Ports.default: PortDisplayOverrides(id=UUID("e4dedb66-0638-4f0c-9941-6420bfe353b2"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1966.960664819945, y=223.1684037396122), width=480, height=180
    )
