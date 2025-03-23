from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeInputDisplay, NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition, NodeOutputWorkflowReference

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("eb72f89e-f831-4fc1-a54f-dec7f429fff9")
    target_handle_id = UUID("52b9ff71-e090-4c68-a713-fd72d194b992")
    output_id = UUID("4dc6e13e-92ba-436e-aa35-87e258f2f585")
    output_name = "final-output"
    node_input_id = UUID("0d184119-05b8-4551-a01c-418d3b983880")
    node_input_display = NodeInputDisplay(
        id=UUID("4dc6e13e-92ba-436e-aa35-87e258f2f585"),
        name="node_input",
        type="STRING",
        value=NodeOutputWorkflowReference(
            node_id="d0538e54-b623-4a71-a5cd-24b1ed5ce223", node_output_id="c66c362b-bb83-4333-a691-b72dc9a8734d"
        ),
    )
    node_input_ids_by_name = {"node_input": UUID("0d184119-05b8-4551-a01c-418d3b983880")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("4dc6e13e-92ba-436e-aa35-87e258f2f585"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2750, y=211.25540166204985), width=471, height=234)
