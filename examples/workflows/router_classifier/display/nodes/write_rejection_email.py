from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.write_rejection_email import WriteRejectionEmail


class WriteRejectionEmailDisplay(BaseInlinePromptNodeDisplay[WriteRejectionEmail]):
    label = "Write Rejection Email"
    node_id = UUID("f4b37571-f8af-48b4-ac02-9a6515dcf0f4")
    output_id = UUID("05c32c54-865b-46f9-b68b-1c295ae1b619")
    array_output_id = UUID("6270aae8-b312-4e9d-905e-fbe5f23d25e4")
    target_handle_id = UUID("75a77dde-080f-406f-afb8-7c7d74df4757")
    node_input_ids_by_name = {"resume_evaluation": UUID("438aafbc-cb61-4b32-b5d6-1cf4f62a5db4")}
    output_display = {
        WriteRejectionEmail.Outputs.text: NodeOutputDisplay(
            id=UUID("05c32c54-865b-46f9-b68b-1c295ae1b619"), name="text"
        ),
        WriteRejectionEmail.Outputs.results: NodeOutputDisplay(
            id=UUID("6270aae8-b312-4e9d-905e-fbe5f23d25e4"), name="results"
        ),
        WriteRejectionEmail.Outputs.json: NodeOutputDisplay(
            id=UUID("0bb9effe-1d07-436d-8ae6-7529b75ec76e"), name="json"
        ),
    }
    port_displays = {
        WriteRejectionEmail.Ports.default: PortDisplayOverrides(id=UUID("6a94190e-f7e0-43d8-8e56-f05c366e3681"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2053, y=1518), width=480, height=261, comment=NodeDisplayComment(expanded=True)
    )
