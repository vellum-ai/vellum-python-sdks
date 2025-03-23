from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeInputDisplay, NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition, WorkflowInputWorkflowReference

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("b0d2bd58-fa00-4eea-98fb-bc09ee1427dd")
    target_handle_id = UUID("ddb7fe0e-0500-4862-8d0d-b05645283c28")
    output_id = UUID("d8381526-1225-4843-8c22-eec7747445e4")
    output_name = "final-output"
    node_input_id = UUID("8a2dbefa-0722-4989-8cb7-f2eb526b3247")
    node_input_display = NodeInputDisplay(
        id=UUID("d8381526-1225-4843-8c22-eec7747445e4"),
        name="node_input",
        type="STRING",
        value=WorkflowInputWorkflowReference(input_variable_id="5f64210f-ec43-48ce-ae40-40a9ba4c4c11"),
    )
    node_input_ids_by_name = {"node_input": UUID("8a2dbefa-0722-4989-8cb7-f2eb526b3247")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("d8381526-1225-4843-8c22-eec7747445e4"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2750, y=210), width=464, height=234)
