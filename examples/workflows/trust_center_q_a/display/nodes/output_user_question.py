from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.output_user_question import OutputUserQuestion


class OutputUserQuestionDisplay(BaseFinalOutputNodeDisplay[OutputUserQuestion]):
    label = "Output: User Question"
    node_id = UUID("12c866ee-27f8-4b1a-a664-034dfa69c789")
    target_handle_id = UUID("998b1e72-aa65-4f7a-8bfd-78f944b60d0b")
    output_name = "question"
    node_input_ids_by_name = {"node_input": UUID("092da64e-5021-492d-8ccb-333c9602f423")}
    output_display = {
        OutputUserQuestion.Outputs.value: NodeOutputDisplay(
            id=UUID("c2fb17c7-f6aa-44b0-a4f1-805f46e058c9"), name="value"
        )
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2341.90612872579, y=-239.41100749518978),
        width=453,
        height=362,
        comment=NodeDisplayComment(expanded=True),
    )
