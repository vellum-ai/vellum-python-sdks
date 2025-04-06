from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.take_best_response import TakeBestResponse


class TakeBestResponseDisplay(BaseInlinePromptNodeDisplay[TakeBestResponse]):
    label = "Take Best Response"
    node_id = UUID("8aaede70-9024-46bc-9ffe-2247baa43eb1")
    output_id = UUID("818b9849-3e2d-4149-b982-860f0d18b9cc")
    array_output_id = UUID("97641cc0-9ea0-4fd9-87f2-df0808a8928f")
    target_handle_id = UUID("335b9eb8-dc2d-419f-ab1d-5af0cb68d434")
    node_input_ids_by_name = {
        "question": UUID("9ae1e761-85f7-46f7-9478-e95eecfdeb87"),
        "support_bot_response_1": UUID("26a360de-e06e-4bbd-bc05-c6dc3f96b538"),
        "support_bot_response_2": UUID("62a38935-9b81-4379-b58a-768185ad6a5a"),
    }
    output_display = {
        TakeBestResponse.Outputs.text: NodeOutputDisplay(id=UUID("818b9849-3e2d-4149-b982-860f0d18b9cc"), name="text"),
        TakeBestResponse.Outputs.results: NodeOutputDisplay(
            id=UUID("97641cc0-9ea0-4fd9-87f2-df0808a8928f"), name="results"
        ),
        TakeBestResponse.Outputs.json: NodeOutputDisplay(id=UUID("7fa84843-cc89-444c-9e5b-64c4270b2448"), name="json"),
    }
    port_displays = {
        TakeBestResponse.Ports.default: PortDisplayOverrides(id=UUID("ee9cdb4f-85d0-48dc-8691-032bb08a2bb0"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=5038.966133246463, y=1237.2432353873394), width=480, height=283
    )
