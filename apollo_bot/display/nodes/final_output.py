from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("2c368766-015e-4d2f-8f57-01937038a4b2")
    target_handle_id = UUID("af15d1e2-2ea2-485c-933a-142db6f9b2d4")
    output_name = "path_taken"
    node_input_ids_by_name = {"node_input": UUID("287431be-000d-498d-9dd0-b8dddbce5a5a")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("f04ec2cc-fd32-42b7-aac8-273bfaa3a283"), name="value")
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2674, y=61),
        z_index=13,
        width=298,
        height=92,
        icon="vellum:icon:circle-stop",
        color="teal",
        comment=NodeDisplayComment(expanded=True, value="Returns the path taken as workflow output."),
    )
