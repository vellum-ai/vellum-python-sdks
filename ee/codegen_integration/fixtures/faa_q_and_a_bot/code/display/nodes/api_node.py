from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseAPINodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides

from ...nodes.api_node import APINode


class APINodeDisplay(BaseAPINodeDisplay[APINode]):
    label = "API Node"
    node_id = UUID("81246ab6-153a-4c87-9f28-b6c28c915cf1")
    target_handle_id = UUID("8f6f1b95-dd80-46dd-b1f6-167196baf697")
    additional_header_key_input_ids = {}
    additional_header_value_input_ids = {}
    node_input_ids_by_name = {
        "url": UUID("20932275-1a55-455f-b481-5895f9e28123"),
        "method": UUID("96d6ea69-24b7-4e5a-94ed-4c4eb3fcfe69"),
        "json": UUID("379f9c64-cad2-4b7d-ba30-32599ec1fe64"),
        "authorization_type": UUID("e29070d6-bd22-46c8-ae18-b6f056ca15ad"),
        "bearer_token_value": UUID("a596f1fc-01a8-467e-9007-19073a98660d"),
        "api_key_header_key": UUID("bcf3aac0-536e-42d5-b666-22cfe40eae98"),
        "api_key_header_value": UUID("bc73ee61-ca29-48fe-b3f2-fea5d8f638f6"),
    }
    attribute_ids_by_name = {"timeout": UUID("bd625080-9c90-43b5-8093-d12977814df8")}
    port_displays = {APINode.Ports.default: PortDisplayOverrides(id=UUID("5fd01b0b-f0fb-488b-a9c7-4ba1dd7df80e"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3916.027261439447, y=917.3816601522587), width=455, height=230
    )
