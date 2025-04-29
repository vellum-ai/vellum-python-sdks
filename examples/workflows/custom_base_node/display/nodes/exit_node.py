from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.exit_node import ExitNode


class ExitNodeDisplay(BaseFinalOutputNodeDisplay[ExitNode]):
    label = "Exit Node"
    node_id = UUID("c69f1216-3000-4e69-afa4-4269c734c980")
    target_handle_id = UUID("674e0ef5-8563-466f-9209-93bb4689082f")
    output_name = "answer"
    node_input_ids_by_name = {"node_input": UUID("72f69630-7210-47ae-be3b-0b6a04a4488f")}
    output_display = {
        ExitNode.Outputs.value: NodeOutputDisplay(id=UUID("708005f3-81e0-4886-95e9-ccb0d6c029d3"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=None, height=None)
