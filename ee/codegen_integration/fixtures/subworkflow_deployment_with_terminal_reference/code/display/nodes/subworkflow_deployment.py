from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseSubworkflowDeploymentNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.subworkflow_deployment import SubworkflowDeployment


class SubworkflowDeploymentDisplay(BaseSubworkflowDeploymentNodeDisplay[SubworkflowDeployment]):
    node_id = UUID("008a5fdb-2a53-404b-b772-32f5bfb77e4f")
    target_handle_id = UUID("0eaa10d3-2805-4e7f-ad97-804124289662")
    output_display = {
        SubworkflowDeployment.Outputs.feedback: NodeOutputDisplay(
            id=UUID("deployed-output-feedback-id"), name="feedback"
        )
    }
    port_displays = {
        SubworkflowDeployment.Ports.default: PortDisplayOverrides(id=UUID("cc328564-987d-4bf3-8d02-9386cbae4aad"))
    }
