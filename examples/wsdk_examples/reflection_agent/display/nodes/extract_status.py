from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.extract_status import ExtractStatus


class ExtractStatusDisplay(BaseTemplatingNodeDisplay[ExtractStatus]):
    label = "Extract Status"
    node_id = UUID("44ae99f5-9cfa-4393-a962-14fc7ad8007d")
    target_handle_id = UUID("b6b76984-3847-44c4-8265-67392ed6d7d0")
    node_input_ids_by_name = {
        "inputs.example_var_1": UUID("06a652ac-d29e-42cb-9e94-4ee91edd644a"),
        "template": UUID("256e6809-8e58-4d0d-89c2-03edcf32865c"),
    }
    output_display = {
        ExtractStatus.Outputs.result: NodeOutputDisplay(id=UUID("45c66eb9-c77d-43c5-86cf-f8e4f03962d8"), name="result")
    }
    port_displays = {ExtractStatus.Ports.default: PortDisplayOverrides(id=UUID("ba254914-762d-45e3-92d5-cf23c5111ca3"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3086.8233673760724, y=284.1854915525598), width=452, height=229
    )
