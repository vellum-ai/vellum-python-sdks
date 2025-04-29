from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.final_output_email_content import FinalOutputEmailContent


class FinalOutputEmailContentDisplay(BaseFinalOutputNodeDisplay[FinalOutputEmailContent]):
    label = "Final Output - Email Content"
    node_id = UUID("879336fa-8d2f-49c7-91e7-1d5ecead8224")
    target_handle_id = UUID("47efd3cb-b7cc-44e7-a7a7-c1294e5b668a")
    output_name = "email_copy"
    node_input_ids_by_name = {"node_input": UUID("259f0fd9-e59f-4825-aa8b-4df60c6d64ec")}
    output_display = {
        FinalOutputEmailContent.Outputs.value: NodeOutputDisplay(
            id=UUID("84803d2a-ca83-40a3-b138-d8ebf64f8af1"), name="value"
        )
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2663, y=954), width=452, height=347, comment=NodeDisplayComment(expanded=True)
    )
