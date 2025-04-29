from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from .....nodes.invoke_functions.nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("ef28df31-7f49-4307-8735-9f179bd92389")
    target_handle_id = UUID("699a3ea9-a074-4d04-b5e1-94943adfcebf")
    output_name = "final-output"
    node_input_ids_by_name = {"node_input": UUID("4a1541b1-d58f-4ec1-81df-dc175e227847")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("fe14414b-f4de-4f26-9339-63e3fab65ce8"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=1830, y=60.5), width=None, height=None)
