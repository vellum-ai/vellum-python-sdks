from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.tool_calling_node import ToolCallingNode


class ToolCallingNodeDisplay(BaseNodeDisplay[ToolCallingNode]):
    label = "Tool Calling Node"
    node_id = UUID("ae6eb941-9219-4646-820c-dee950813c97")
    attribute_ids_by_name = {
        "ml_model": UUID("c632581f-2400-4e5e-97d9-34712506aac6"),
        "prompt_inputs": UUID("db105c70-3822-4c6a-9c6b-95707578428c"),
        "blocks": UUID("67253c21-4fb4-40f2-bbd6-08d6ca4b0a3f"),
        "parameters": UUID("982a3b8f-88b0-44df-8307-2294e917baa7"),
        "settings": UUID("53974d83-5f61-4331-90ac-f5aa7846718c"),
        "max_prompt_iterations": UUID("77e4f54b-d400-4d4b-bad4-17521b3bf5f6"),
    }
    output_display = {
        ToolCallingNode.Outputs.text: NodeOutputDisplay(id=UUID("c13b57f2-636a-439d-a97d-1bcc2bf4a69a"), name="text"),
        ToolCallingNode.Outputs.chat_history: NodeOutputDisplay(
            id=UUID("aba54e31-73e8-4a13-b54a-5d39769b474e"), name="chat_history"
        ),
    }
    port_displays = {
        ToolCallingNode.Ports.default: PortDisplayOverrides(id=UUID("67098afd-6adc-4f5a-8572-754d91a49b67"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1748.7748197987958, y=-824.3311297770466), width=None, height=None
    )
