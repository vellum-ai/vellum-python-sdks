from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ....nodes.email_sender import EmailSender


class EmailSenderDisplay(BaseNodeDisplay[EmailSender]):
    label = "Email_sender"
    node_id = UUID("5c1670eb-e046-4488-bbb7-e64fd1751735")
    attribute_ids_by_name = {
        "ml_model": UUID("9f4cc3b2-ba99-4adf-aaec-3f347021377a"),
        "prompt_inputs": UUID("706ffc34-9521-4df8-9ef0-59bc4522d817"),
        "blocks": UUID("a65a4b8c-e17b-495e-8606-fd4e1c7cb394"),
        "parameters": UUID("ae95c24f-50c3-49b5-bdae-dbfeafbd17c6"),
        "settings": UUID("3c5c835c-bebd-4f76-8f0e-39451a6cf9e2"),
        "max_prompt_iterations": UUID("a39799fe-be37-45d2-a2b8-7f8271686836"),
        "functions": UUID("92049098-059d-4fc0-a11d-10b573d532df"),
    }
    output_display = {
        EmailSender.Outputs.text: NodeOutputDisplay(id=UUID("4b732dcf-9286-4cd5-8d5e-abc02778251f"), name="text"),
        EmailSender.Outputs.chat_history: NodeOutputDisplay(
            id=UUID("980f79a2-6081-400f-9fba-eaaf5c140606"), name="chat_history"
        ),
    }
    port_displays = {EmailSender.Ports.default: PortDisplayOverrides(id=UUID("9f750c68-3e28-4d77-b542-f2d6a42b7105"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1609.0911318850603, y=642.6621263386281), width=None, height=None
    )
