from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeInputDisplay, NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition, NodeOutputWorkflowReference

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("a9455dc7-85f5-43a9-8be7-f131bc5f08e2")
    target_handle_id = UUID("0ef13a41-8905-45ad-9aee-09c201368981")
    output_id = UUID("493cfa4b-5235-4b71-99ef-270955f35fcb")
    output_name = "final-output"
    node_input_id = UUID("ff856e07-ed9a-47fa-8cec-76ebd8795cdb")
    node_input_display = NodeInputDisplay(
        id=UUID("493cfa4b-5235-4b71-99ef-270955f35fcb"),
        name="node_input",
        type="NUMBER",
        value=NodeOutputWorkflowReference(
            node_id="c207b440-6aac-4047-a37c-e25fcb5b9cfb", node_output_id="0e455862-ccc4-47a4-a9a5-061fadc94fd6"
        ),
    )
    node_input_ids_by_name = {"node_input": UUID("ff856e07-ed9a-47fa-8cec-76ebd8795cdb")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("493cfa4b-5235-4b71-99ef-270955f35fcb"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2750, y=210), width=458, height=234)
