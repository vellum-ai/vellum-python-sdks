from uuid import UUID

from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EntrypointDisplay,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowMetaDisplay,
    WorkflowOutputDisplay,
)
from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay

from ..nodes.final_output import FinalOutput
from ..nodes.merge_node import MergeNode
from ..nodes.templating_node_1 import TemplatingNode1
from ..nodes.templating_node_2 import TemplatingNode2
from ..nodes.templating_node_3 import TemplatingNode3
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("b8b9eb69-4af1-4953-b576-aa59eb138696"),
        entrypoint_node_source_handle_id=UUID("1095ae85-1e2f-4433-aacf-fac30fe12ff3"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-799.056805115941, y=229.9501405115533, zoom=0.5596719538849867)
        ),
    )
    entrypoint_displays = {
        TemplatingNode2: EntrypointDisplay(
            id=UUID("b8b9eb69-4af1-4953-b576-aa59eb138696"),
            edge_display=EdgeDisplay(id=UUID("22106f5d-fd97-431d-9615-48278f7a954b")),
        ),
        TemplatingNode1: EntrypointDisplay(
            id=UUID("b8b9eb69-4af1-4953-b576-aa59eb138696"),
            edge_display=EdgeDisplay(id=UUID("2c4d2583-af8d-4fd8-972b-c850325d4158")),
        ),
    }
    edge_displays = {
        (TemplatingNode2.Ports.default, MergeNode): EdgeDisplay(
            id=UUID("114b1eab-ad2a-4612-b590-35f6ebdd87bc"), z_index=None
        ),
        (MergeNode.Ports.default, TemplatingNode3): EdgeDisplay(
            id=UUID("fba82107-15bc-4033-9b38-6a8b0094aa7f"), z_index=None
        ),
        (TemplatingNode3.Ports.default, FinalOutput): EdgeDisplay(
            id=UUID("0c6ddc01-1db6-4b0f-ac7c-8b43ca4cf3c2"), z_index=None
        ),
        (TemplatingNode1.Ports.default, MergeNode): EdgeDisplay(
            id=UUID("20c8d251-bcf1-497e-8d37-668e661ccabc"), z_index=None
        ),
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("8988fa40-5083-4635-a647-bcbbf42c1652"), name="final-output"
        )
    }
