from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.final_output_2 import FinalOutput2


class FinalOutput2Display(BaseFinalOutputNodeDisplay[FinalOutput2]):
    label = "Final Output 2"
    node_id = UUID("f9c5254c-b86d-420d-811a-a1674df273cd")
    target_handle_id = UUID("87d73dc6-cafd-4f8b-b2fd-8367baba5d61")
    output_id = UUID("8c6e5464-8916-4039-b911-cf707855d372")
    output_name = "answer"
    node_input_id = UUID("4a999b21-0555-404c-a4f4-c613cd108450")
    node_input_ids_by_name = {"node_input": UUID("4a999b21-0555-404c-a4f4-c613cd108450")}
    output_display = {
        FinalOutput2.Outputs.value: NodeOutputDisplay(id=UUID("8c6e5464-8916-4039-b911-cf707855d372"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=5134, y=443), width=480, height=271)
