from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseAPINodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.api_node import APINode


class APINodeDisplay(BaseAPINodeDisplay[APINode]):
    url_input_id = UUID("20932275-1a55-455f-b481-5895f9e28123")
    method_input_id = UUID("96d6ea69-24b7-4e5a-94ed-4c4eb3fcfe69")
    body_input_id = UUID("379f9c64-cad2-4b7d-ba30-32599ec1fe64")
    authorization_type_input_id = UUID("e29070d6-bd22-46c8-ae18-b6f056ca15ad")
    bearer_token_value_input_id = UUID("a596f1fc-01a8-467e-9007-19073a98660d")
    api_key_header_key_input_id = UUID("bcf3aac0-536e-42d5-b666-22cfe40eae98")
    api_key_header_value_input_id = UUID("bc73ee61-ca29-48fe-b3f2-fea5d8f638f6")
    text_output_id = UUID("0c945315-0607-4ef6-8051-f4b6498e9526")
    json_output_id = UUID("c3c38fac-f413-4dad-863d-3d388231ba22")
    status_code_output_id = UUID("4d3e2c1d-ac9f-43a4-81fc-b652239986a0")
    additional_header_key_input_ids = {}
    additional_header_value_input_ids = {}
    node_input_ids_by_name = {
        "method": UUID("96d6ea69-24b7-4e5a-94ed-4c4eb3fcfe69"),
        "url": UUID("20932275-1a55-455f-b481-5895f9e28123"),
        "body": UUID("379f9c64-cad2-4b7d-ba30-32599ec1fe64"),
        "authorization_type": UUID("e29070d6-bd22-46c8-ae18-b6f056ca15ad"),
        "bearer_token_value": UUID("a596f1fc-01a8-467e-9007-19073a98660d"),
        "api_key_header_key": UUID("bcf3aac0-536e-42d5-b666-22cfe40eae98"),
        "api_key_header_value": UUID("bc73ee61-ca29-48fe-b3f2-fea5d8f638f6"),
    }
    port_displays = {APINode.Ports.default: PortDisplayOverrides(id=UUID("5fd01b0b-f0fb-488b-a9c7-4ba1dd7df80e"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3916.027261439447, y=917.3816601522587), width=455, height=230
    )
