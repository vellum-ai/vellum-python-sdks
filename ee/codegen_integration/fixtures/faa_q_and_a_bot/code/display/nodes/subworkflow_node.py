from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseSubworkflowDeploymentNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.subworkflow_node import SubworkflowNode


class SubworkflowNodeDisplay(BaseSubworkflowDeploymentNodeDisplay[SubworkflowNode]):
    node_id = UUID("ddb58eb1-f089-4bb0-b4b9-f630411c0acf")
    target_handle_id = UUID("d96bb2c2-1c6f-4e7d-9163-c6b16a67e1f2")
    node_input_ids_by_name = {"subworkflow_inputs.chat_history": UUID("76519b3c-285d-425d-ba7a-ce7300e4ed9c")}
    output_display = {
        SubworkflowNode.Outputs.chat_history: NodeOutputDisplay(
            id=UUID("53970e88-0bf6-4364-86b3-840d78a2afe5"), name="chat_history"
        )
    }
    port_displays = {
        SubworkflowNode.Ports.default: PortDisplayOverrides(id=UUID("de5b0a72-e46f-4534-89a9-b78725694dd2"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=3914, y=631))
