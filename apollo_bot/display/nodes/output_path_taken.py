from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.output_path_taken import OutputPathTaken


class OutputPathTakenDisplay(BaseTemplatingNodeDisplay[OutputPathTaken]):
    label = "Output Path Taken"
    node_id = UUID("e55788e3-4d8b-4026-8c39-d8e4e738a8b8")
    target_handle_id = UUID("c705d5a4-98fa-4cbb-ab54-4d755e69bd3b")
    node_input_ids_by_name = {
        "template": UUID("96069bff-ba26-4ed2-8711-19edaad4ad10"),
        "inputs.is_tagged": UUID("4e77da75-a017-4449-9db2-d92d13cd1d25"),
    }
    output_display = {
        OutputPathTaken.Outputs.result: NodeOutputDisplay(
            id=UUID("0add3944-81cf-4508-b28c-11db268ecbe5"), name="result"
        )
    }
    port_displays = {
        OutputPathTaken.Ports.default: PortDisplayOverrides(id=UUID("f105bcfc-1478-47bc-bf07-a4158943c858"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2198, y=59),
        z_index=12,
        width=330,
        height=96,
        icon="vellum:icon:stamp",
        color="brown",
        comment=NodeDisplayComment(expanded=True, value="Templates the result indicating which path was taken."),
    )
