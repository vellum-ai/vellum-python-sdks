from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeInputDisplay, NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition, NodeOutputWorkflowReference

from ...nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("54803ff7-9afd-4eb1-bff3-242345d3443d")
    target_handle_id = UUID("6bf50c29-d2f5-4a4f-a63b-907c9053833d")
    output_id = UUID("f1eca494-a7dc-41c0-9c74-9658a64955e6")
    output_name = "final-output"
    node_input_id = UUID("960ac634-0081-4e20-9ab8-c98b826fbfc6")
    node_input_display = NodeInputDisplay(
        id=UUID("f1eca494-a7dc-41c0-9c74-9658a64955e6"),
        name="node_input",
        type="STRING",
        value=NodeOutputWorkflowReference(
            node_id="1645c7e7-1b5f-4ca3-9610-0c5ac30a77ff", node_output_id="13e677d3-14e7-4b0c-ab36-834bb99c930c"
        ),
    )
    node_input_ids_by_name = {"node_input": UUID("960ac634-0081-4e20-9ab8-c98b826fbfc6")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("f1eca494-a7dc-41c0-9c74-9658a64955e6"), name="value")
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2761.0242006615217, y=208.9757993384785), width=474, height=234
    )
