from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("81a1c8a8-6b65-4ba8-b14a-0b2e70aed8f1")
    target_handle_id = UUID("36d04318-1779-40fa-81fb-ae14ba87d1d6")
    output_id = UUID("3ae9132d-cbb9-4237-ac5b-9c80096eaac5")
    output_name = "final-output"
    node_input_id = UUID("fa56b746-783e-43a6-9c12-61d89cfb6f77")
    node_input_ids_by_name = {"node_input": UUID("fa56b746-783e-43a6-9c12-61d89cfb6f77")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("3ae9132d-cbb9-4237-ac5b-9c80096eaac5"), name="value")
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1465.3578490588761, y=635.1421509411235), width=450, height=239
    )
