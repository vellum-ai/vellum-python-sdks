from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.write_next_round_email import WriteNextRoundEmail


class WriteNextRoundEmailDisplay(BaseInlinePromptNodeDisplay[WriteNextRoundEmail]):
    label = "Write Next Round Email"
    node_id = UUID("ac302d25-409e-4649-afdc-2ba2ac7f16ac")
    output_id = UUID("050b67a9-7976-433c-961b-65c3591c1e17")
    array_output_id = UUID("f1809bf4-8f1c-44c0-ad94-9412b4cdd428")
    target_handle_id = UUID("dde07670-5e53-4cc1-ac3f-ec19d6a050e6")
    node_input_ids_by_name = {"resume_evaluation": UUID("0681162b-315a-4ff4-a5ba-4f205c902538")}
    output_display = {
        WriteNextRoundEmail.Outputs.text: NodeOutputDisplay(
            id=UUID("050b67a9-7976-433c-961b-65c3591c1e17"), name="text"
        ),
        WriteNextRoundEmail.Outputs.results: NodeOutputDisplay(
            id=UUID("f1809bf4-8f1c-44c0-ad94-9412b4cdd428"), name="results"
        ),
        WriteNextRoundEmail.Outputs.json: NodeOutputDisplay(
            id=UUID("f124ede6-09e1-4605-bbc5-4601604dba61"), name="json"
        ),
    }
    port_displays = {
        WriteNextRoundEmail.Ports.default: PortDisplayOverrides(id=UUID("8e11f04a-e42a-4638-9564-a998c0950958"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2053, y=692), width=480, height=261, comment=NodeDisplayComment(expanded=True)
    )
