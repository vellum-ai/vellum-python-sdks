from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseCodeExecutionNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.code_execution_node_9 import CodeExecutionNode9


class CodeExecutionNode9Display(BaseCodeExecutionNodeDisplay[CodeExecutionNode9]):
    label = "Code Execution Node 9"
    node_id = UUID("4248d980-8b1f-41c3-aa1f-782960451437")
    target_handle_id = UUID("50436d14-1453-49ad-a5f4-dabb5267e825")
    output_id = UUID("3124e5d7-8687-4086-8e47-d051c4d96f77")
    log_output_id = UUID("18b02207-805a-46b9-a96c-ed7c970f39a5")
    node_input_ids_by_name = {
        "code": UUID("5a3814df-9235-40bb-ba3b-fe1a778855de"),
        "runtime": UUID("186093c2-067d-4fc0-8b8e-d2b8bd0ebf34"),
    }
    output_display = {
        CodeExecutionNode9.Outputs.result: NodeOutputDisplay(
            id=UUID("3124e5d7-8687-4086-8e47-d051c4d96f77"), name="result"
        ),
        CodeExecutionNode9.Outputs.log: NodeOutputDisplay(id=UUID("18b02207-805a-46b9-a96c-ed7c970f39a5"), name="log"),
    }
    port_displays = {
        CodeExecutionNode9.Ports.default: PortDisplayOverrides(id=UUID("76309d77-de31-45f4-8312-73f7f4a54b6a"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1192.6215641478343, y=-689.5438654528195), width=554, height=256
    )
