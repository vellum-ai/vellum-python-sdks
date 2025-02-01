from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseSubworkflowDeploymentNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.subworkflow_deployment import SubworkflowDeployment


class SubworkflowDeploymentDisplay(BaseSubworkflowDeploymentNodeDisplay[SubworkflowDeployment]):
    label = "Subworkflow Deployment"
    node_id = UUID("07d76e33-f3df-4235-8493-07e341208bf5")
    target_handle_id = UUID("30771282-5c0a-4a98-a3a8-4c7eeda30d23")
    node_input_ids_by_name = {"test": UUID("97b63d71-5413-417f-9cf5-49e1b4fd56e4")}
    output_display = {
        SubworkflowDeployment.Outputs.final_output: NodeOutputDisplay(
            id=UUID("61759cf7-da3d-45a3-9f73-68d3907207ae"), name="final-output"
        )
    }
    port_displays = {
        SubworkflowDeployment.Ports.default: PortDisplayOverrides(id=UUID("fc38b3bd-5c08-4729-9e37-211c415637ad"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1873.116343490305, y=239.74958448753466), width=None, height=None
    )
