from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.agent_response import AgentResponse


class AgentResponseDisplay(BaseFinalOutputNodeDisplay[AgentResponse]):
    label = "Agent Response"
    node_id = UUID("b3b8ff28-ce7d-4078-a4b2-5a6ad4426758")
    target_handle_id = UUID("d28743ce-0ec5-4bab-bfbb-1f0d192bcb0b")
    output_id = UUID("23f727b7-d00e-48df-8387-f1ea21e1bcb6")
    output_name = "response"
    node_input_id = UUID("4da6d59e-d509-491d-b814-a76aa5dbabc9")
    node_input_ids_by_name = {"node_input": UUID("4da6d59e-d509-491d-b814-a76aa5dbabc9")}
    output_display = {
        AgentResponse.Outputs.value: NodeOutputDisplay(id=UUID("23f727b7-d00e-48df-8387-f1ea21e1bcb6"), name="value")
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3406.0443370687376, y=1734.0619423765406),
        width=457,
        height=306,
        comment=NodeDisplayComment(expanded=True),
    )
