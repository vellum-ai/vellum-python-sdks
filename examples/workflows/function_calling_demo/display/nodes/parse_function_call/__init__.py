# flake8: noqa: F401, F403

from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlineSubworkflowNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ....nodes.parse_function_call import ParseFunctionCall
from .nodes import *
from .workflow import *


class ParseFunctionCallDisplay(BaseInlineSubworkflowNodeDisplay[ParseFunctionCall]):
    label = "Parse Function Call"
    node_id = UUID("345d09e7-0117-4aef-aba4-ac7f3ce1b4a7")
    target_handle_id = UUID("f5f2f53a-4867-4bf0-b07b-8b39d39c6a03")
    workflow_input_ids_by_name = {}
    output_display = {
        ParseFunctionCall.Outputs.function_args: NodeOutputDisplay(
            id=UUID("d520f0a1-c28f-4007-acf9-2758871f2250"), name="function-args"
        ),
        ParseFunctionCall.Outputs.function_name: NodeOutputDisplay(
            id=UUID("680f2d8d-b03a-43b9-9d77-626044e03227"), name="function-name"
        ),
        ParseFunctionCall.Outputs.tool_id: NodeOutputDisplay(
            id=UUID("764c26a4-b0c4-4a52-9e19-96e651eccbd3"), name="tool-id"
        ),
    }
    port_displays = {
        ParseFunctionCall.Ports.default: PortDisplayOverrides(id=UUID("b0b8c13c-4c55-4c38-9e00-412000f517b3"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2850, y=75), width=None, height=None)
