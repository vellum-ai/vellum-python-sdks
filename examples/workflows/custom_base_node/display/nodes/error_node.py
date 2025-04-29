from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseErrorNodeDisplay

from ...nodes.error_node import ErrorNode


class ErrorNodeDisplay(BaseErrorNodeDisplay[ErrorNode]):
    name = "error-node"
    node_id = UUID("92e401f1-110f-4edc-8bb0-cad879e1ea08")
    label = "Error Node"
    # error_output_id = UUID("None")
    target_handle_id = UUID("c1b30829-76af-4d99-bf83-b030c551a7cf")
    node_input_ids_by_name = {"error_source_input_id": UUID("02d8ab87-a237-4892-81bc-9e532c73064e")}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=None, height=None)
