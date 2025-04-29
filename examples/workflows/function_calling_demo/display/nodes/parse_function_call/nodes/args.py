from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from .....nodes.parse_function_call.nodes.args import Args


class ArgsDisplay(BaseFinalOutputNodeDisplay[Args]):
    label = "Args"
    node_id = UUID("2bb745c2-6405-4c79-9659-c35bf6a0331a")
    target_handle_id = UUID("b1eb4d88-5d4e-473a-bf74-e86e6f5b5c71")
    output_name = "function-args"
    node_input_ids_by_name = {"node_input": UUID("37038db4-ad28-4270-a256-32302a0962e1")}
    output_display = {
        Args.Outputs.value: NodeOutputDisplay(id=UUID("d520f0a1-c28f-4007-acf9-2758871f2250"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=5535, y=345), width=None, height=None)
