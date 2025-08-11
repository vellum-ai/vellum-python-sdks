from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ....nodes.tool_calling_node_1 import ToolCallingNode


class ToolCallingNodeDisplay(BaseNodeDisplay[ToolCallingNode]):
    label = "ToolCallingNode"
    node_id = UUID("66600077-8097-4fd0-8372-90c2d74a1a91")
    attribute_ids_by_name = {
        "ml_model": UUID("bad8c7de-e4ad-416d-b25e-afcd55c959b5"),
        "prompt_inputs": UUID("1e2205bf-c75d-4bf0-a137-9f567dc3204f"),
        "blocks": UUID("22044661-7f73-4624-9c43-35a1b160ccfa"),
        "parameters": UUID("f2cce915-8c6b-43f9-84a5-c6a05e15487e"),
        "settings": UUID("e139aad1-7894-4ed6-9062-5bd838e1e9c4"),
        "max_prompt_iterations": UUID("3f6ee4e9-f3a2-4a6e-8a87-71e4e35a0cb1"),
        "functions": UUID("3e51fa9b-1712-4fa7-8d9c-f8b14dcfd5a4"),
    }
    output_display = {
        ToolCallingNode.Outputs.text: NodeOutputDisplay(id=UUID("ebebf72f-3b1c-4e86-a1d7-c5e1c03d9056"), name="text"),
        ToolCallingNode.Outputs.chat_history: NodeOutputDisplay(
            id=UUID("7935e0e2-ea38-4339-9242-73ee16c6c9f2"), name="chat_history"
        ),
    }
    port_displays = {
        ToolCallingNode.Ports.default: PortDisplayOverrides(id=UUID("c0fb9226-88c1-43ae-9c36-4a9a4bccfe93"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1454.0949597059173, y=-89.86733882137577), width=None, height=None
    )
