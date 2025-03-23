from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeInputDisplay, NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition, NodeOutputWorkflowReference

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("ed688426-1976-4d0c-9f3a-2a0b0fae161a")
    target_handle_id = UUID("b28439f6-0c1e-44c0-87b1-b7fa3c7408b2")
    output_id = UUID("43e128f4-24fe-4484-9d08-948a4a390707")
    output_name = "final-output"
    node_input_id = UUID("097798e5-9330-46a4-b8ec-e93532668d37")
    node_input_display = NodeInputDisplay(
        id=UUID("43e128f4-24fe-4484-9d08-948a4a390707"),
        name="node_input",
        type="STRING",
        value=NodeOutputWorkflowReference(
            node_id="e5ff9360-a29c-437b-a9c1-05fc52df2834", node_output_id="d56d7c49-7b45-4933-9779-2bd7f82c2141"
        ),
    )
    node_input_ids_by_name = {"node_input": UUID("097798e5-9330-46a4-b8ec-e93532668d37")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("43e128f4-24fe-4484-9d08-948a4a390707"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2750, y=210), width=480, height=234)
