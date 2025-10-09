from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ....nodes.fetch_slack_message_node import FetchSlackMessageNode


class FetchSlackMessageNodeDisplay(BaseNodeDisplay[FetchSlackMessageNode]):
    label = "FetchSlackMessageNode"
    node_id = UUID("abc456c9-efe5-4a35-a727-44d068c5d759")
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1174.9208847469042, y=311.6551998547142),
        z_index=10,
        icon="vellum:icon:wrench",
        color="teal",
    )
    attribute_ids_by_name = {
        "ml_model": UUID("5e0148b3-288e-4def-b00d-2908b0f23c98"),
        "blocks": UUID("e692d3c2-4a79-4b00-b247-6b60ef857e69"),
        "prompt_inputs": UUID("560ca81f-61fe-4b4c-83b0-b46dfa91f3cb"),
        "parameters": UUID("610a1acd-b16f-42c9-8aa6-25c8b8c156e5"),
        "functions": UUID("f630818f-a284-4f04-af0b-5b199e93a816"),
        "max_prompt_iterations": UUID("275ae078-e31f-4212-80b6-513e00ab5055"),
        "settings": UUID("c58a922c-8343-444a-a234-b7b775d98111"),
    }
    output_display = {
        FetchSlackMessageNode.Outputs.text: NodeOutputDisplay(
            id=UUID("7ef8460f-56d0-4b97-aed7-823a7b7358e7"), name="text"
        ),
        FetchSlackMessageNode.Outputs.chat_history: NodeOutputDisplay(
            id=UUID("add65235-481f-44a4-a797-b1daa3d9dbc1"), name="chat_history"
        ),
    }
    port_displays = {
        FetchSlackMessageNode.Ports.default: PortDisplayOverrides(id=UUID("c0d74769-2576-41e2-96b2-0dc00750254d"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1174.9208847469042, y=311.6551998547142),
        z_index=10,
        icon="vellum:icon:wrench",
        color="teal",
    )
