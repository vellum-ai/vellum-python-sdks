from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    node_id = UUID("0c3546e8-2f41-4d18-9ec3-b9c4dc13e248")
    target_handle_id = UUID("d2ae6fcd-b803-4f30-bf8b-0f5b2f049d92")
    output_name = "feedback"
    node_input_ids_by_name = {"node_input": UUID("ac83e418-5435-4710-aa81-6dab6c1bf0e3")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("d373db7e-fb81-45b1-a9e6-14e57ea570c8"), name="value"),
    }
    display_data = NodeDisplayData(width=471, height=234)
