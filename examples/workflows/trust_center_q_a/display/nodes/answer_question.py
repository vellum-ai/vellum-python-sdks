from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.answer_question import AnswerQuestion


class AnswerQuestionDisplay(BaseInlinePromptNodeDisplay[AnswerQuestion]):
    label = "Answer Question"
    node_id = UUID("645ebed4-8dcf-41ed-924a-5f7ce436fe0e")
    output_id = UUID("b910a43e-864f-48b4-b57c-e9924d51807b")
    array_output_id = UUID("010e1f65-2080-4391-9d1d-a0eaea832021")
    target_handle_id = UUID("30ad35f8-ebba-4364-979d-96ba74211898")
    node_input_ids_by_name = {
        "prompt_inputs.chat_history": UUID("6c0b6479-ea6a-4302-958b-22ad1d630efb"),
        "prompt_inputs.context": UUID("5e50c27e-4d76-496e-b8ea-98f185308376"),
    }
    attribute_ids_by_name = {"ml_model": UUID("9fc7da77-c986-44da-ab04-9c78ed73a3e5")}
    output_display = {
        AnswerQuestion.Outputs.text: NodeOutputDisplay(id=UUID("b910a43e-864f-48b4-b57c-e9924d51807b"), name="text"),
        AnswerQuestion.Outputs.results: NodeOutputDisplay(
            id=UUID("010e1f65-2080-4391-9d1d-a0eaea832021"), name="results"
        ),
        AnswerQuestion.Outputs.json: NodeOutputDisplay(id=UUID("904d5bcf-e96c-4ec0-af7f-6e6f11e3af3f"), name="json"),
    }
    port_displays = {
        AnswerQuestion.Ports.default: PortDisplayOverrides(id=UUID("f5c5f06b-3dbc-4864-9f04-f97950ede5b1"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3575.284864660129, y=357.82013225823766),
        width=480,
        height=296,
        comment=NodeDisplayComment(expanded=True),
    )
