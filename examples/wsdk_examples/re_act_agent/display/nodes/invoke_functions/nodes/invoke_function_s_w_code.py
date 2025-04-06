from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseCodeExecutionNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from .....nodes.invoke_functions.nodes.invoke_function_s_w_code import InvokeFunctionSWCode


class InvokeFunctionSWCodeDisplay(BaseCodeExecutionNodeDisplay[InvokeFunctionSWCode]):
    label = "Invoke Function(s) w/ Code"
    node_id = UUID("afc576f7-4075-4093-8f03-3690269bd5dd")
    target_handle_id = UUID("c2aa8438-f7ad-4ec8-bde7-3405fda310db")
    output_id = UUID("3a9030eb-c061-40e4-96ce-db7b776b88a4")
    log_output_id = UUID("c80a1ece-b349-41d0-81c2-8171de0859d2")
    node_input_ids_by_name = {
        "code_inputs.fn_call": UUID("72474d8f-5626-47ff-8832-948d5ab27417"),
        "code": UUID("f1e76b3e-b925-4d7c-8faf-9161413b9411"),
        "runtime": UUID("3a3a2f3d-02c5-4d41-8fc0-994cb87fe263"),
    }
    output_display = {
        InvokeFunctionSWCode.Outputs.result: NodeOutputDisplay(
            id=UUID("3a9030eb-c061-40e4-96ce-db7b776b88a4"), name="result"
        ),
        InvokeFunctionSWCode.Outputs.log: NodeOutputDisplay(
            id=UUID("c80a1ece-b349-41d0-81c2-8171de0859d2"), name="log"
        ),
    }
    port_displays = {
        InvokeFunctionSWCode.Ports.default: PortDisplayOverrides(id=UUID("e6c1ff26-3f3e-4167-a5ee-9043385824f8"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=610, y=0), width=None, height=None)
