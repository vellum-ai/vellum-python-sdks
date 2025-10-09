from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ....nodes.reply_in_slack_node import ReplyInSlackNode


class ReplyInSlackNodeDisplay(BaseNodeDisplay[ReplyInSlackNode]):
    label = "ReplyInSlackNode"
    node_id = UUID("91a40900-98e8-42b6-8937-d046648a503e")
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2658, y=245), z_index=15, icon="vellum:icon:wrench", color="teal"
    )
    attribute_ids_by_name = {
        "ml_model": UUID("89f3ff89-7d82-43e6-bbff-1ae024ce2212"),
        "blocks": UUID("cbf3bb0a-f283-431d-a2d5-d5f1bae2195d"),
        "prompt_inputs": UUID("b8e6850e-d9d8-4960-b478-84e434d3e9a3"),
        "parameters": UUID("cd64472c-bb47-4f2f-be1d-551644915708"),
        "functions": UUID("2dae4090-5327-4ffd-8322-6149745e92c5"),
        "max_prompt_iterations": UUID("0d1c30c1-3408-4a95-b987-5dd41c67af86"),
        "settings": UUID("a6bded78-4012-4c88-8611-ebb1c65b41a4"),
    }
    output_display = {
        ReplyInSlackNode.Outputs.text: NodeOutputDisplay(id=UUID("7fc3c4de-3e78-4610-8835-8f114cec5777"), name="text"),
        ReplyInSlackNode.Outputs.chat_history: NodeOutputDisplay(
            id=UUID("0ff909c3-6dda-4951-81b1-df809150b2d9"), name="chat_history"
        ),
    }
    port_displays = {
        ReplyInSlackNode.Ports.default: PortDisplayOverrides(id=UUID("25ecaaac-5e3d-4c67-8761-4dcf2031625c"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2658, y=245), z_index=15, icon="vellum:icon:wrench", color="teal"
    )
