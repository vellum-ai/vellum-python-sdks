from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseSubworkflowDeploymentNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.subworkflow_deployment import SubworkflowDeployment


class SubworkflowDeploymentDisplay(BaseSubworkflowDeploymentNodeDisplay[SubworkflowDeployment]):
    node_id = UUID("subworkflow-deployment-node-id")
    target_handle_id = UUID("subworkflow-target-handle")
    output_display = {
        SubworkflowDeployment.Outputs.feedback: NodeOutputDisplay(
            id=UUID("deployed-output-feedback-id"), name="feedback"
        )
    }
    port_displays = {SubworkflowDeployment.Ports.default: PortDisplayOverrides(id=UUID("subworkflow-source-handle"))}
