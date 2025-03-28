from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.extract_score import ExtractScore


class ExtractScoreDisplay(BaseTemplatingNodeDisplay[ExtractScore]):
    label = "Extract Score"
    node_id = UUID("8421f554-d065-426d-a5b8-a24e713b54da")
    target_handle_id = UUID("15d6a18b-baab-4191-9524-524188c707ba")
    node_input_ids_by_name = {
        "inputs.resume_score_json": UUID("420a5f4e-dcb1-44eb-906d-34a11691dd1d"),
        "template": UUID("2db22841-9572-4df7-8d34-b8cf5bcb7678"),
    }
    output_display = {
        ExtractScore.Outputs.result: NodeOutputDisplay(id=UUID("406969db-7950-40a7-8077-53638995103b"), name="result")
    }
    port_displays = {ExtractScore.Ports.default: PortDisplayOverrides(id=UUID("b13925a1-dff7-4354-9fb7-0832979e2240"))}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=864, y=1177), width=458, height=229)
