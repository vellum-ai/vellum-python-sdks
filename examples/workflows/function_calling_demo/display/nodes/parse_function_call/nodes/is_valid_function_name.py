from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseCodeExecutionNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from .....nodes.parse_function_call.nodes.is_valid_function_name import IsValidFunctionName


class IsValidFunctionNameDisplay(BaseCodeExecutionNodeDisplay[IsValidFunctionName]):
    label = "Is Valid Function Name"
    node_id = UUID("644b84f0-2e9f-4ca3-b91d-0f63d431ce2f")
    target_handle_id = UUID("d41fa741-3e2f-4d6b-8608-d6ab6926e01f")
    output_id = UUID("377c6fd6-73de-4cf6-8437-f12738f9b077")
    log_output_id = UUID("dd1ea277-eaec-4c59-b5ed-23017940b5f5")
    node_input_ids_by_name = {
        "code_inputs.function_name": UUID("cc496e6f-4983-4db0-96fd-36e6976bcd8d"),
        "code_inputs.allowed_function_names": UUID("131d9183-afcf-446b-b1f6-9979cad15858"),
        "code": UUID("d498be92-0470-4c47-b9d4-5087e54a8116"),
        "runtime": UUID("a8098cf8-d647-4495-9f3c-24b43fabf979"),
    }
    output_display = {
        IsValidFunctionName.Outputs.result: NodeOutputDisplay(
            id=UUID("377c6fd6-73de-4cf6-8437-f12738f9b077"), name="result"
        ),
        IsValidFunctionName.Outputs.log: NodeOutputDisplay(id=UUID("dd1ea277-eaec-4c59-b5ed-23017940b5f5"), name="log"),
    }
    port_displays = {
        IsValidFunctionName.Ports.default: PortDisplayOverrides(id=UUID("0d1a598d-d40f-41fa-8025-c81e188647b4"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=4050, y=960), width=None, height=None)
