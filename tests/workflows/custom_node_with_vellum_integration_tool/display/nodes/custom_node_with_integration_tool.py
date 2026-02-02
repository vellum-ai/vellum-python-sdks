from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides

from ...nodes.custom_node_with_integration_tool import CustomNodeWithIntegrationTool


class CustomNodeWithIntegrationToolDisplay(BaseNodeDisplay[CustomNodeWithIntegrationTool]):
    node_id = UUID("042c2c7e-cc36-4cd7-a609-b159d97229de")
    attribute_ids_by_name = {"tool": UUID("81579e88-4d3a-412b-98fe-24be8801d569")}
    port_displays = {
        CustomNodeWithIntegrationTool.Ports.default: PortDisplayOverrides(
            id=UUID("71f4dcff-d1e4-4c5a-90b9-7feaa67927f0")
        )
    }
