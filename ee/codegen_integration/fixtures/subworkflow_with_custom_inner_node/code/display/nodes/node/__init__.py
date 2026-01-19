# flake8: noqa: F401, F403

from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlineSubworkflowNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from . import workflow
from ....nodes.node import MySubworkflowNode
from .nodes import *


class MySubworkflowNodeDisplay(BaseInlineSubworkflowNodeDisplay[MySubworkflowNode]):
    label = "My Node"
    node_id = UUID("04fea948-6682-47b8-8646-bab40e720038")
    target_handle_id = UUID("9dec56e2-4ac1-4040-b0a5-0b1b395a8af2")
    workflow_input_ids_by_name = {}
    output_display = {
        MySubworkflowNode.Outputs.result: NodeOutputDisplay(
            id=UUID("4b59eb8b-8f00-4e8f-91d6-423eff3d4663"), name="result"
        )
    }
    port_displays = {
        MySubworkflowNode.Ports.default: PortDisplayOverrides(id=UUID("0cb70d33-28e5-4d90-ad50-f3b59f6ed4b1"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=470, y=0),
        z_index=2,
        width=370,
        height=124,
        comment=NodeDisplayComment(expanded=True, value="An inline subworkflow node."),
    )
