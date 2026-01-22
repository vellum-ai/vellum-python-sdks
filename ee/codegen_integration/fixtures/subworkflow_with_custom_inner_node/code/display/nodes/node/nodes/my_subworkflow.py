from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from .....nodes.node.nodes.my_subworkflow import MySubworkflowNode


class MySubworkflowNodeDisplay(BaseNodeDisplay[MySubworkflowNode]):
    node_id = UUID("fce721b0-2e11-4070-9acd-502292dd682b")
    output_display = {
        MySubworkflowNode.Outputs.result: NodeOutputDisplay(
            id=UUID("eadbf483-a1de-4287-9b8a-3624901c856f"), name="result"
        )
    }
    port_displays = {
        MySubworkflowNode.Ports.default: PortDisplayOverrides(id=UUID("675ad077-fa40-42b3-a0f9-7770b0371755"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=0, y=0))
