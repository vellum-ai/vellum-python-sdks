from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.output_answer import OutputAnswer


class OutputAnswerDisplay(BaseFinalOutputNodeDisplay[OutputAnswer]):
    label = "Output: Answer"
    node_id = UUID("deb0823c-20eb-4cb6-8445-636d37a9c58e")
    target_handle_id = UUID("df4f459e-c3e4-4ae4-ae33-69145f0d2b50")
    output_name = "answer"
    node_input_ids_by_name = {"node_input": UUID("eb02ccd1-a768-4fa8-adde-dff1f335a265")}
    output_display = {
        OutputAnswer.Outputs.value: NodeOutputDisplay(id=UUID("519d3b9b-4caa-4928-abd1-ce3130caabee"), name="value")
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=4140.211433566075, y=326.3319690467531),
        width=464,
        height=325,
        comment=NodeDisplayComment(expanded=True),
    )
