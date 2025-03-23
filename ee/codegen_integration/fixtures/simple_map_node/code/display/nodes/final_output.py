from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeInputDisplay, NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition, NodeOutputWorkflowReference

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("fa0d5829-f259-4db8-a11a-b12fd7237ea5")
    target_handle_id = UUID("8e19172a-4f87-4c21-8c91-ccdfb3e74c16")
    output_id = UUID("d9269719-a7a2-4388-9b85-73e329a78d16")
    output_name = "final-output"
    node_input_id = UUID("ca8f8a34-24d3-4941-893f-73c5e3bbb66c")
    node_input_display = NodeInputDisplay(
        id=UUID("d9269719-a7a2-4388-9b85-73e329a78d16"),
        name="node_input",
        type="JSON",
        value=NodeOutputWorkflowReference(
            node_id="72cb9f1e-aedd-47af-861e-4f38d27053b6", node_output_id="bffc4749-00b8-44db-90ee-db655cbc7e62"
        ),
    )
    node_input_ids_by_name = {"node_input": UUID("ca8f8a34-24d3-4941-893f-73c5e3bbb66c")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("d9269719-a7a2-4388-9b85-73e329a78d16"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=864, y=58.5), width=454, height=234)
