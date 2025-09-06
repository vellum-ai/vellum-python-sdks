from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.templating_node_3 import TemplatingNode3


class TemplatingNode3Display(BaseTemplatingNodeDisplay[TemplatingNode3]):
    label = "Templating Node"
    node_id = UUID("7f7823e9-b97a-4bbe-bfcf-40aed8db24c9")
    target_handle_id = UUID("2c1e39e0-ce3e-4c2d-8baf-c5d93b244997")
    node_input_ids_by_name = {
        "template": UUID("c1cc89c9-7cb7-498d-9dda-e9e5f36fe556"),
        "inputs.input_a": UUID("56ff5b3f-41e1-492d-80a0-493f170452a1"),
        "inputs.input_b": UUID("553fe161-a16e-48d1-b07c-b51fe7d10bf3"),
    }
    output_display = {
        TemplatingNode3.Outputs.result: NodeOutputDisplay(
            id=UUID("a18fbec8-4530-4ca9-a265-e9323dc45fc4"), name="result"
        )
    }
    port_displays = {
        TemplatingNode3.Ports.default: PortDisplayOverrides(id=UUID("e51cd1b6-6c1f-4436-aaed-36cb38e7615d"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2877.183015927978, y=185.8336045706372), width=480, height=278
    )
