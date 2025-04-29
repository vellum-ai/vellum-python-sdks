from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseErrorNodeDisplay

from .....nodes.parse_function_call.nodes.error_node_1 import ErrorNode2


class ErrorNode2Display(BaseErrorNodeDisplay[ErrorNode2]):
    name = "error-node"
    node_id = UUID("0dde89cd-b006-48f4-a5cb-03f4898d4dee")
    label = "Error Node"
    error_output_id = UUID("9df35350-bbf0-471f-9d6d-6316c6cb87ea")
    target_handle_id = UUID("d78e9d18-cc2f-47fa-98d0-040320be29a0")
    node_input_ids_by_name = {"error_source_input_id": UUID("5efc9a7e-5138-4cb7-91e2-4618dd5bfdcc")}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=3150, y=225), width=None, height=None)
