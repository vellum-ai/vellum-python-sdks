from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseInlineSubworkflowNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ....nodes.subworkflow_node import SubworkflowNode


class SubworkflowNodeDisplay(BaseInlineSubworkflowNodeDisplay[SubworkflowNode]):
    label = "Subworkflow Node"
    node_id = UUID("8c6d5fe5-e955-4598-9c35-0cd6f5eca47e")
    target_handle_id = UUID("67ee54dc-2505-4368-8e67-70d89ac2a9e5")
    workflow_input_ids_by_name = {}
    node_input_ids_by_name = {}
    port_displays = {
        SubworkflowNode.Ports.default: PortDisplayOverrides(id=UUID("fa5c22bc-2499-43fa-880f-75fb20d0587f"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1991.684833859175, y=178.94753425793772), width=None, height=None
    )
