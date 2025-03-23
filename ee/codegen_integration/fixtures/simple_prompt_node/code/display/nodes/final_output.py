from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeInputDisplay, NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition, NodeOutputWorkflowReference

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("e39c8f13-d59b-49fc-8c59-03ee7997b9b6")
    target_handle_id = UUID("77ab6d0c-7fea-441e-8e22-7afc62b3555b")
    output_id = UUID("aed7279d-59cd-4c15-b82c-21de48129ba3")
    output_name = "final-output"
    node_input_id = UUID("cfed56e1-bdf8-4e17-a0f9-ff1bb8ca4221")
    node_input_display = NodeInputDisplay(
        id=UUID("aed7279d-59cd-4c15-b82c-21de48129ba3"),
        name="node_input",
        type="STRING",
        value=NodeOutputWorkflowReference(
            node_id="7e09927b-6d6f-4829-92c9-54e66bdcaf80", node_output_id="2d4f1826-de75-499a-8f84-0a690c8136ad"
        ),
    )
    node_input_ids_by_name = {"node_input": UUID("cfed56e1-bdf8-4e17-a0f9-ff1bb8ca4221")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("aed7279d-59cd-4c15-b82c-21de48129ba3"), name="value")
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2761.0242006615217, y=208.9757993384785), width=474, height=234
    )
