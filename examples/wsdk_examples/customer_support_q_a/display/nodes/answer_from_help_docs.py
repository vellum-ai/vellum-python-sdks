from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.answer_from_help_docs import AnswerFromHelpDocs


class AnswerFromHelpDocsDisplay(BaseInlinePromptNodeDisplay[AnswerFromHelpDocs]):
    label = "Answer from HelpDocs"
    node_id = UUID("b6192292-e521-4e52-8fbb-3a276a967c9b")
    output_id = UUID("d142f5b3-2d37-4985-acee-36145aeb7f37")
    array_output_id = UUID("7474b519-c47d-4fc6-9f00-0bd3c9a550d5")
    target_handle_id = UUID("c98a61e2-782d-4f37-a0b7-02b4fdfc8367")
    node_input_ids_by_name = {
        "context_str": UUID("dc9d9831-85b0-4046-ac16-1f74ecd5ed54"),
        "customer_question": UUID("f05cec45-79ae-466c-a961-75c63c73f7a0"),
    }
    output_display = {
        AnswerFromHelpDocs.Outputs.text: NodeOutputDisplay(
            id=UUID("d142f5b3-2d37-4985-acee-36145aeb7f37"), name="text"
        ),
        AnswerFromHelpDocs.Outputs.results: NodeOutputDisplay(
            id=UUID("7474b519-c47d-4fc6-9f00-0bd3c9a550d5"), name="results"
        ),
        AnswerFromHelpDocs.Outputs.json: NodeOutputDisplay(
            id=UUID("34356498-0c5c-4632-b493-91c5318065e0"), name="json"
        ),
    }
    port_displays = {
        AnswerFromHelpDocs.Ports.default: PortDisplayOverrides(id=UUID("5dddc604-7f31-47cc-a410-95e2cd35d78b"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3944.7967556188532, y=1657.0257545187833), width=480, height=229
    )
