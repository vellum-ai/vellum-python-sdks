from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from .....nodes.invoke_functions.nodes.function_result_context import FunctionResultContext


class FunctionResultContextDisplay(BaseTemplatingNodeDisplay[FunctionResultContext]):
    label = "Function Result + Context"
    node_id = UUID("02805736-ea32-437b-92f0-bfc637208194")
    target_handle_id = UUID("5140dd48-cb28-4fc3-85f3-b6d5c3d2ca1d")
    node_input_ids_by_name = {
        "template": UUID("67df1a2d-6388-46a4-9cd3-ffb337cd09c0"),
        "inputs.item": UUID("3dad5510-c33d-40d5-8056-460d77bcb962"),
        "inputs.fxn_result": UUID("9cfea597-d0ad-48e6-b538-1e0e4ec7df1f"),
    }
    output_display = {
        FunctionResultContext.Outputs.result: NodeOutputDisplay(
            id=UUID("3846c00b-97d5-4ca4-b98f-1001a769a94c"), name="result"
        )
    }
    port_displays = {
        FunctionResultContext.Ports.default: PortDisplayOverrides(id=UUID("4d6d2327-4619-46cb-9be2-b1b92738af50"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=1220, y=26.5), width=None, height=None)
