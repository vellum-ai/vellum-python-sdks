from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("e39c8f13-d59b-49fc-8c59-03ee7997b9b6")
    target_handle_id = UUID("77ab6d0c-7fea-441e-8e22-7afc62b3555b")
    output_id = UUID("aed7279d-59cd-4c15-b82c-21de48129ba3")
    output_name = "final-output"
    node_input_id = UUID("cfed56e1-bdf8-4e17-a0f9-ff1bb8ca4221")
    node_input_ids_by_name = {"node_input": UUID("cfed56e1-bdf8-4e17-a0f9-ff1bb8ca4221")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("aed7279d-59cd-4c15-b82c-21de48129ba3"), name="value")
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2761.0242006615217, y=208.9757993384785), width=474, height=234
    )
