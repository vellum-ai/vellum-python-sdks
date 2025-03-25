from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from .....nodes.subworkflow_node.nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("f3fe1e6e-5a4a-42d8-9cfe-9ecbcb935f72")
    target_handle_id = UUID("20aa0107-742b-4662-941f-4f146b3c5565")
    output_id = UUID("6ab3665f-881d-488b-9124-a6da40136c68")
    output_name = "final-output"
    node_input_id = UUID("8e8c6182-4898-47de-be8f-769edad990ed")
    node_input_ids_by_name = {"node_input": UUID("8e8c6182-4898-47de-be8f-769edad990ed")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("6ab3665f-881d-488b-9124-a6da40136c68"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2750, y=208.7778595317725), width=456, height=233)
