from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.function_calls_to_json_array import FunctionCallsToJSONArray


class FunctionCallsToJSONArrayDisplay(BaseTemplatingNodeDisplay[FunctionCallsToJSONArray]):
    label = "Function Calls to JSON Array"
    node_id = UUID("9d3bd2de-db69-4125-9c97-f481585dd2bc")
    target_handle_id = UUID("b6df9c97-a4ba-459f-86cb-6564efc1b49a")
    node_input_ids_by_name = {
        "template": UUID("5e333970-1e58-41de-a023-9f5507c47f56"),
        "inputs.prompt_outputs": UUID("edebf277-4ebb-4e8e-b813-8302df576791"),
    }
    output_display = {
        FunctionCallsToJSONArray.Outputs.result: NodeOutputDisplay(
            id=UUID("17b64233-4e00-44e2-8e9a-5b44411e99a3"), name="result"
        )
    }
    port_displays = {
        FunctionCallsToJSONArray.Ports.default: PortDisplayOverrides(id=UUID("c028325f-d175-4b06-8bed-61f293054585"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2723.468320846336, y=-31.27078140449322), width=457, height=229
    )
