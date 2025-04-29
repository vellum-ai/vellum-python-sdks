from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.evaluator_agent import EvaluatorAgent


class EvaluatorAgentDisplay(BaseInlinePromptNodeDisplay[EvaluatorAgent]):
    label = "Evaluator Agent"
    node_id = UUID("c213d5e3-24ef-4f0f-83de-83fb2ab8291e")
    output_id = UUID("5a8639b1-1735-4287-9d33-fc9dc01dc652")
    array_output_id = UUID("b1487507-9d8d-4a15-a572-d831e7bc3b65")
    target_handle_id = UUID("a61907e2-6acf-4877-9f57-38b685cb37d6")
    node_input_ids_by_name = {
        "math_problem": UUID("618cc457-9779-4a91-baa4-1aea562c0a65"),
        "proposed_solution": UUID("d0b8e3c7-9c74-4f11-b527-8b6f0f4ecc21"),
    }
    output_display = {
        EvaluatorAgent.Outputs.text: NodeOutputDisplay(id=UUID("5a8639b1-1735-4287-9d33-fc9dc01dc652"), name="text"),
        EvaluatorAgent.Outputs.results: NodeOutputDisplay(
            id=UUID("b1487507-9d8d-4a15-a572-d831e7bc3b65"), name="results"
        ),
        EvaluatorAgent.Outputs.json: NodeOutputDisplay(id=UUID("0741b7b3-8dae-49bb-99ac-2508b8436e11"), name="json"),
    }
    port_displays = {
        EvaluatorAgent.Ports.default: PortDisplayOverrides(id=UUID("1ffb5ac8-5a14-4ba6-9a72-d25da938c27c"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2564.5326176251383, y=219.6964613495673),
        width=480,
        height=409,
        comment=NodeDisplayComment(expanded=True),
    )
