from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.has_function_calls import HasFunctionCalls


class HasFunctionCallsDisplay(BaseTemplatingNodeDisplay[HasFunctionCalls]):
    label = "Has Function Calls?"
    node_id = UUID("6ff4b3bb-5b5a-4e82-997d-4a2014cb188c")
    target_handle_id = UUID("6fc3b953-c49b-45a7-a105-3b6bdf564e05")
    node_input_ids_by_name = {
        "template": UUID("8fbf4bb9-2a09-4a4b-80d2-0bc07527b26c"),
        "inputs.output": UUID("8d2192a3-6bc9-47a6-b758-c6c4d890fc5f"),
    }
    output_display = {
        HasFunctionCalls.Outputs.result: NodeOutputDisplay(
            id=UUID("dfc5d492-eaae-4570-b0bc-22324e5a5171"), name="result"
        )
    }
    port_displays = {
        HasFunctionCalls.Ports.default: PortDisplayOverrides(id=UUID("d579d27d-835d-4bf9-a678-44f63de59a8c"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=1485, y=-40.873739776839415), width=453, height=229)
