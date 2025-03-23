from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeInputDisplay, NodeOutputDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition, NodeOutputWorkflowReference

from .....nodes.map_node.nodes.final_output import FinalOutput


class FinalOutputDisplay(BaseFinalOutputNodeDisplay[FinalOutput]):
    label = "Final Output"
    node_id = UUID("d9d29911-dd45-45d5-9ac8-1a06bb596c2f")
    target_handle_id = UUID("8ff89a09-6ff0-4b02-bba7-eb8456a9c865")
    output_id = UUID("bffc4749-00b8-44db-90ee-db655cbc7e62")
    output_name = "final-output"
    node_input_id = UUID("18dddbce-025b-461c-aa7a-ab2561739521")
    node_input_display = NodeInputDisplay(
        id=UUID("bffc4749-00b8-44db-90ee-db655cbc7e62"),
        name="node_input",
        type="STRING",
        value=NodeOutputWorkflowReference(
            node_id="4b0a7578-e5ec-4d72-b396-62abdecbd101", node_output_id="503aa2c1-6b99-43e8-98f7-1fef458a8d29"
        ),
    )
    node_input_ids_by_name = {"node_input": UUID("18dddbce-025b-461c-aa7a-ab2561739521")}
    output_display = {
        FinalOutput.Outputs.value: NodeOutputDisplay(id=UUID("bffc4749-00b8-44db-90ee-db655cbc7e62"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2750, y=210), width=463, height=234)
