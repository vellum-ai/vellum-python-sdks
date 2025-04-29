from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from .....nodes.parse_function_call.nodes.name import Name


class NameDisplay(BaseFinalOutputNodeDisplay[Name]):
    label = "Name"
    node_id = UUID("fa12bb7f-c8e4-4d5d-9916-c348109c0ffb")
    target_handle_id = UUID("a435166f-a65a-40a4-95e7-ad7def5491d2")
    output_name = "function-name"
    node_input_ids_by_name = {"node_input": UUID("d2ecd03e-b443-482c-838a-2dc345dbf8ed")}
    output_display = {
        Name.Outputs.value: NodeOutputDisplay(id=UUID("680f2d8d-b03a-43b9-9d77-626044e03227"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=5520, y=-135), width=None, height=None)
