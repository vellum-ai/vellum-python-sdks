from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseAPINodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.api_node import ApiNode


class ApiNodeDisplay(BaseAPINodeDisplay[ApiNode]):
    label = "API Node"
    node_id = UUID("743aec59-2aa9-402c-963a-d9b86a80a1c2")
    target_handle_id = UUID("fd10e0db-0130-4fdc-8fc7-146eafe1b470")
    additional_header_key_input_ids = {
        "test": UUID("7dbd1729-ec2e-4be5-a868-e542ba421115"),
        "nom": UUID("4e7557f4-16ec-4fec-97a6-fe221eae1ee5"),
    }
    additional_header_value_input_ids = {
        "test": UUID("a7a796b5-ac5b-471d-af20-b45c66b699ce"),
        "nom": UUID("58099189-1676-4d89-a01d-9c1d79ba833a"),
    }
    node_input_ids_by_name = {
        "method": UUID("4bc3ec8f-f889-45c2-bad0-5498f28cc8af"),
        "url": UUID("d2f4547b-eaa3-4b9a-a0f7-0da0975d4e11"),
        "json": UUID("65dbcf74-183a-49e0-b553-2a3d25ad741d"),
        "authorization_type": UUID("c9b08ce9-2dfc-4cbe-9e65-0bf6f8e248c0"),
        "bearer_token_value": UUID("6d330109-ec8e-4c39-af30-63d77f07c35d"),
        "api_key_header_key": UUID("908e1fb5-bcba-4388-ae1d-a53d256eda97"),
        "api_key_header_value": UUID("efefc4f7-6c95-4561-b7a0-b48533e0c68f"),
        "additional_header_key": UUID("4e7557f4-16ec-4fec-97a6-fe221eae1ee5"),
        "additional_header_value": UUID("58099189-1676-4d89-a01d-9c1d79ba833a"),
    }
    attribute_ids_by_name = {"timeout": UUID("63c3fb19-534a-4a75-b868-35e42a9e866b")}
    output_display = {
        ApiNode.Outputs.json: NodeOutputDisplay(id=UUID("f6f469ae-3f50-4276-a294-43d8d0fcf477"), name="json"),
        ApiNode.Outputs.status_code: NodeOutputDisplay(
            id=UUID("6ab9d555-7007-43e1-9f90-d2ca21ea99cf"), name="status_code"
        ),
        ApiNode.Outputs.text: NodeOutputDisplay(id=UUID("6a3c1704-7020-411d-a440-84b2a481691e"), name="text"),
    }
    port_displays = {ApiNode.Ports.default: PortDisplayOverrides(id=UUID("b8ad3fd2-c96c-4ae8-8eae-d234fb13a139"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1889.865705614568, y=236.61265174506826),
        width=467,
        height=288,
        comment=NodeDisplayComment(expanded=True),
    )
