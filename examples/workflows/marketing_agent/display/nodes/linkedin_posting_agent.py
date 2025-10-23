from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.linkedin_posting_agent import LinkedinPostingAgent


class LinkedinPostingAgentDisplay(BaseNodeDisplay[LinkedinPostingAgent]):
    label = "Linkedin Posting Agent"
    node_id = UUID("3aadb9ac-a5c6-4960-9627-262960984992")
    attribute_ids_by_name = {
        "ml_model": UUID("ab0eac48-be30-49da-a674-31c8c828e67c"),
        "prompt_inputs": UUID("5b2d808a-e558-4f5d-90c8-a1293f909831"),
        "blocks": UUID("20405f19-213b-4799-8bd5-37e063b2e136"),
        "parameters": UUID("0afd5553-6d62-4c01-add2-c37cdf650203"),
        "settings": UUID("dd6061db-ff7b-4d57-a597-cd191b68a0db"),
        "max_prompt_iterations": UUID("9b72d4c5-74d3-4688-9ce1-9b8893872457"),
    }
    output_display = {
        LinkedinPostingAgent.Outputs.text: NodeOutputDisplay(
            id=UUID("9ad5d163-0fe6-44f9-99f9-094bd9c2b061"), name="text"
        ),
        LinkedinPostingAgent.Outputs.chat_history: NodeOutputDisplay(
            id=UUID("69d49f08-00eb-498f-93aa-45c3c6a60c64"), name="chat_history"
        ),
    }
    port_displays = {
        LinkedinPostingAgent.Ports.default: PortDisplayOverrides(id=UUID("a1fbc799-17be-4c22-ae03-e2fb87d3e945"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2734.822493213279, y=-1345.3362426053889), width=None, height=None
    )
