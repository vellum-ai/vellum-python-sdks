from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseErrorNodeDisplay

from ...nodes.error_node import ErrorNode


class ErrorNodeDisplay(BaseErrorNodeDisplay[ErrorNode]):
    name = "error-node"
    node_id = UUID("456afdb9-4d76-40b8-a032-0bddf0583632")
    label = "Error Node"
    error_output_id = UUID("8fd34ccf-aadb-4fab-b450-11b247737548")
    target_handle_id = UUID("a815d06f-b3af-46de-a53b-b2e38f0e3ea3")
    node_input_ids_by_name = {"error_source_input_id": UUID("d88e2764-a9b0-4b13-aa04-d7a5bdd54785")}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=4260, y=780), width=364, height=124)
