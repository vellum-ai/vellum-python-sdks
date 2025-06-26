from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseCodeExecutionNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.code_execution_node import CodeExecutionNode


class CodeExecutionNodeDisplay(BaseCodeExecutionNodeDisplay[CodeExecutionNode]):
    target_handle_id = UUID("3a82ede9-4b1b-42fc-84a0-10e91de602dc")
    output_id = UUID("98ef146c-6603-4930-85c2-8a637a58476c")
    log_output_id = UUID("ce51ac26-1e30-4434-9915-429b55ed9f06")
    label = "Code Execution Node"
    node_id = UUID("cdec50ed-5cfc-418e-ad1f-45ef7a0abe4b")
    node_input_ids_by_name = {
        "code_inputs.arg1": UUID("b7081865-838c-49e3-baa8-388272e359a4"),
        "code": UUID("e5a9379e-871d-4a8f-88cd-b3ea832577dc"),
        "runtime": UUID("611d4cd9-dca8-4821-8d3b-899439c556bb"),
    }
    output_display = {
        CodeExecutionNode.Outputs.result: NodeOutputDisplay(
            id=UUID("98ef146c-6603-4930-85c2-8a637a58476c"), name="result"
        ),
        CodeExecutionNode.Outputs.log: NodeOutputDisplay(id=UUID("ce51ac26-1e30-4434-9915-429b55ed9f06"), name="log"),
    }
    port_displays = {
        CodeExecutionNode.Ports.default: PortDisplayOverrides(id=UUID("734e3a85-f96e-408e-89f1-703bcc486e8a"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1855.8380935218793, y=384.6100572199606), width=480, height=224
    )
