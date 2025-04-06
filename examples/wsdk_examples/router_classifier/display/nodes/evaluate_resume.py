from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.evaluate_resume import EvaluateResume


class EvaluateResumeDisplay(BaseInlinePromptNodeDisplay[EvaluateResume]):
    label = "Evaluate Resume"
    node_id = UUID("b3baf439-997d-470c-a3fa-b7330fa01b59")
    output_id = UUID("0c374fba-f4d8-400f-a1ed-e8716b790d46")
    array_output_id = UUID("5b2b2db7-2456-49f5-99ad-f353303a8228")
    target_handle_id = UUID("77231475-31fd-49f6-8994-dbb64e9f1d6f")
    node_input_ids_by_name = {
        "resume": UUID("3c5dff6d-b4a6-46cf-a3b6-5a7292124ae9"),
        "job_description": UUID("55de0eea-10cd-40a4-853e-78b41e444699"),
    }
    output_display = {
        EvaluateResume.Outputs.text: NodeOutputDisplay(id=UUID("0c374fba-f4d8-400f-a1ed-e8716b790d46"), name="text"),
        EvaluateResume.Outputs.results: NodeOutputDisplay(
            id=UUID("5b2b2db7-2456-49f5-99ad-f353303a8228"), name="results"
        ),
        EvaluateResume.Outputs.json: NodeOutputDisplay(id=UUID("322f30de-626a-46a3-8657-42f7b45d8869"), name="json"),
    }
    port_displays = {
        EvaluateResume.Ports.default: PortDisplayOverrides(id=UUID("ed90f5f2-2acd-4661-9baa-608e18809952"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=254, y=1043.5), width=480, height=333, comment=NodeDisplayComment(expanded=True)
    )
