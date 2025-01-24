from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseErrorNodeDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.error_node import ErrorNode


class ErrorNodeDisplay(BaseErrorNodeDisplay[ErrorNode]):
    name = "error-node"
    node_id = UUID("e5ff9360-a29c-437b-a9c1-05fc52df2834")
    label = "Error Node"
    error_output_id = UUID("77839b3c-fe1c-4dcb-9c61-2fac827f729b")
    target_handle_id = UUID("370d712d-3369-424e-bcf7-f4da1aef3928")
    node_input_ids_by_name = {"error_source_input_id": UUID("f3a0d8b9-7772-4db6-8e28-f49f8c4d9e2a")}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1966.960664819945, y=223.1684037396122), width=480, height=180
    )
