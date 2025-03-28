from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseErrorNodeDisplay

from ...nodes.error_node import ErrorNode


class ErrorNodeDisplay(BaseErrorNodeDisplay[ErrorNode]):
    name = "error-node"
    node_id = UUID("4bcac836-1339-4c1e-8a0f-d1f452258ee7")
    label = "Error Node"
    error_output_id = UUID("40702d6a-624f-40b8-9c79-0a98967484db")
    target_handle_id = UUID("d1118188-af35-40a6-b1f6-f48f0a47002d")
    node_input_ids_by_name = {"error_source_input_id": UUID("84a630a5-fd7a-4672-ae27-bd1e87e44c22")}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=4379.60471538661, y=610.7283212464927), width=364, height=131
    )
