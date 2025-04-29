from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from .....nodes.parse_function_call.nodes.tool_id import ToolID


class ToolIDDisplay(BaseFinalOutputNodeDisplay[ToolID]):
    label = "Tool ID"
    node_id = UUID("b20229cd-8fd7-4cab-8e8f-d3fbaa8f6712")
    target_handle_id = UUID("260b40f0-9fbe-4c84-84f3-aadc01f122f8")
    output_name = "tool-id"
    node_input_ids_by_name = {"node_input": UUID("aa57a708-d7e7-40f9-853d-fc1d66ac62b3")}
    output_display = {
        ToolID.Outputs.value: NodeOutputDisplay(id=UUID("764c26a4-b0c4-4a52-9e19-96e651eccbd3"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=5505, y=825), width=None, height=None)
