from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.templating_node import TemplatingNode


class TemplatingNodeDisplay(BaseTemplatingNodeDisplay[TemplatingNode]):
    label = "Templating Node"
    node_id = UUID("533c6bd8-6088-4abc-a168-8c1758abcd33")
    target_handle_id = UUID("048d310e-1a4d-4038-b534-8c68a4509b93")
    template_input_id = UUID("f97d721a-e685-498e-90c3-9c3d9358fdad")
    node_input_ids_by_name = {
        "example_var_1": UUID("a0d1d7cf-242a-4bd9-a437-d308a7ced9b3"),
        "template": UUID("f97d721a-e685-498e-90c3-9c3d9358fdad"),
    }
    output_display = {
        TemplatingNode.Outputs.result: NodeOutputDisplay(id=UUID("423bc529-1a1a-4f72-af4d-cbdb5f0a5929"), name="result")
    }
    port_displays = {
        TemplatingNode.Ports.default: PortDisplayOverrides(id=UUID("afda9a19-0618-42e1-9b63-5d0db2a88f62"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1970.9393258426965, y=232.4943117977528), width=466, height=224
    )
