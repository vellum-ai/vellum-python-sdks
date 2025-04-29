from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseErrorNodeDisplay

from .....nodes.parse_function_call.nodes.error_node import ErrorNode1


class ErrorNode1Display(BaseErrorNodeDisplay[ErrorNode1]):
    name = "error-node"
    node_id = UUID("2f1c13c1-7ffe-48a2-b1f5-f99d711c3880")
    label = "Error Node"
    error_output_id = UUID("d1c9c405-b96c-4648-bf87-52d7e3898fac")
    target_handle_id = UUID("4f5ecc8a-bf35-4ce3-b4ec-fc7f675da3d9")
    node_input_ids_by_name = {"error_source_input_id": UUID("a3c25a49-cb6e-4d92-abe0-30fcc257d81a")}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=6000, y=1380), width=None, height=None)
