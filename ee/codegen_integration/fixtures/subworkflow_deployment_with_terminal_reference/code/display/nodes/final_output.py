from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    node_id = UUID("terminal-node-id")
    target_handle_id = UUID("terminal-target-handle")
    output_name = "feedback"
    node_input_ids_by_name = {"node_input": "terminal-node-input-id"}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("workflow-output-feedback-id"), name="value"),
    }
    display_data = NodeDisplayData(width=471, height=234)
