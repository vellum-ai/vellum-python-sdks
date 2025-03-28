from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.agent_node import AgentNode


class AgentNodeDisplay(BaseInlinePromptNodeDisplay[AgentNode]):
    label = "Agent Node"
    node_id = UUID("5d28e493-87ff-44f2-afc7-10ece69b798d")
    output_id = UUID("9066d1a1-6662-4e09-996f-7b92aced9b47")
    array_output_id = UUID("0b0d0975-b66f-4163-b8b6-57566b3bf2b6")
    target_handle_id = UUID("bd7137dc-9c30-4881-8b99-b7697b9df11b")
    node_input_ids_by_name = {"chat_history": UUID("7d0d3c27-4faa-42fe-a76f-5e4b934b49e9")}
    output_display = {
        AgentNode.Outputs.text: NodeOutputDisplay(id=UUID("9066d1a1-6662-4e09-996f-7b92aced9b47"), name="text"),
        AgentNode.Outputs.results: NodeOutputDisplay(id=UUID("0b0d0975-b66f-4163-b8b6-57566b3bf2b6"), name="results"),
        AgentNode.Outputs.json: NodeOutputDisplay(id=UUID("6b031f82-7927-42bf-b555-c7191c7733b4"), name="json"),
    }
    port_displays = {AgentNode.Ports.default: PortDisplayOverrides(id=UUID("cc9eaae2-ebe1-41d6-9faa-ac4f5bd01a2e"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=690, y=271.3250297289478),
        width=480,
        height=283,
        comment=NodeDisplayComment(expanded=True),
    )
