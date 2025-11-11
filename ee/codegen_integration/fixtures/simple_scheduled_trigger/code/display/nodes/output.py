from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.output import Output


class OutputDisplay(BaseFinalOutputNodeDisplay[Output]):
    label = "Output"
    node_id = UUID("3eca4d69-3e7c-44fa-a3f9-0d52db9e37e1")
    target_handle_id = UUID("39066076-ece0-4374-83c9-990bcd63b0dd")
    output_name = "output"
    node_input_ids_by_name = {"node_input": UUID("a0f4e11d-85b3-485a-ba10-21c8600142a7")}
    output_display = {
        Output.Outputs.value: NodeOutputDisplay(id=UUID("cb1ba284-84cf-4fb1-a57d-9fdb742646a0"), name="value"),
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=600, y=-20),
        z_index=3,
        width=418,
        height=92,
        icon="vellum:icon:circle-stop",
        color="teal",
    )
