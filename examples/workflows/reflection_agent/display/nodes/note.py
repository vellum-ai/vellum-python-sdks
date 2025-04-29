from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNoteNodeDisplay

from ...nodes.note import Note


class NoteDisplay(BaseNoteNodeDisplay[Note]):
    text = "Note: many of these Prompt Nodes include the full context via Chat History (with Attempts and Evaluator Feedback). This is not mandatory— you may prefer to only send the current solution/evaluation pair to reduce costs and bias. However, including past solution attempts in the context may improve performance. It will depend on your use-case and cost/latency/quality constraints. "
    style = {
        "fontSize": 16,
        "backgroundColor": "#FFEF8A",
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1717.8720479880744, y=-4.0697246951307875), width=560, height=242
    )
