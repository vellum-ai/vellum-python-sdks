from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ....nodes.workflow import ContextAwareToolNode


class ContextAwareToolNodeDisplay(BaseNodeDisplay[ContextAwareToolNode]):
    node_id = UUID("66a8b845-8e84-4918-9188-11f056ae6aca")
    attribute_ids_by_name = {
        "ml_model": UUID("39daad34-7f38-44c1-be75-f94b0944be37"),
        "blocks": UUID("8355d8e0-7995-4607-a026-21674658d969"),
        "functions": UUID("3cfc8fdf-9386-41d3-986e-f8f3fd977989"),
        "prompt_inputs": UUID("081e77ed-fc30-4ccd-931f-85a98fa6cc2e"),
        "parameters": UUID("833e0339-b89c-4245-b6af-1c4135550fa7"),
        "max_prompt_iterations": UUID("468cdae9-8024-4f1c-a483-8f10cc38c963"),
        "settings": UUID("6a8d52ca-d09a-4018-928b-633a5ef201e8"),
    }
    output_display = {
        ContextAwareToolNode.Outputs.json: NodeOutputDisplay(
            id=UUID("c158de75-9c33-49f3-9a27-5d605078534d"), name="json"
        ),
        ContextAwareToolNode.Outputs.text: NodeOutputDisplay(
            id=UUID("aef1a076-b479-44a1-b1e7-06009099c18d"), name="text"
        ),
        ContextAwareToolNode.Outputs.chat_history: NodeOutputDisplay(
            id=UUID("0a83eb44-9035-4d50-92db-d53808e45528"), name="chat_history"
        ),
    }
    port_displays = {
        ContextAwareToolNode.Ports.default: PortDisplayOverrides(id=UUID("f23d7ecf-0bc1-4e14-91be-99f091e9c997"))
    }
    display_data = NodeDisplayData(
        comment=NodeDisplayComment(
            expanded=True, value="\n    A tool calling node with a function that has a WorkflowContext parameter.\n    "
        )
    )
