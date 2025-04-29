from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNoteNodeDisplay

from ...nodes.copy_of_note import CopyOfNote


class CopyOfNoteDisplay(BaseNoteNodeDisplay[CopyOfNote]):
    text = "Trust Center Q&A Bot"
    style = {
        "fontSize": 78,
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1320.589921371261, y=-136.7475345704591), width=890, height=165
    )
