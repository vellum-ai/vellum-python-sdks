from uuid import UUID

from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EntrypointDisplay,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowInputsDisplay,
    WorkflowMetaDisplay,
    WorkflowOutputDisplay,
)
from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay

from ..inputs import Inputs
from ..nodes.code_execution_node import CodeExecutionNode
from ..nodes.final_output import FinalOutput
from ..nodes.map_node import MapNode
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("77325e35-b73e-4596-bfb0-3cf3ddf11a2e"),
        entrypoint_node_source_handle_id=UUID("f342d075-e79a-46ea-8de9-e40ed8152070"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=0, y=151.5), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=224.90864867521066, y=180.0534988628682, zoom=0.6573565995604552)
        ),
    )
    inputs_display = {
        Inputs.items: WorkflowInputsDisplay(id=UUID("cdc4468f-45e7-46ce-bbe7-d1aa9ad86514"), name="items"),
        Inputs.test: WorkflowInputsDisplay(id=UUID("f245af7d-16af-4bdb-8602-e646cbff3407"), name="test"),
    }
    entrypoint_displays = {
        CodeExecutionNode: EntrypointDisplay(
            id=UUID("77325e35-b73e-4596-bfb0-3cf3ddf11a2e"),
            edge_display=EdgeDisplay(id=UUID("ec1f1cb3-7221-4f7d-aaa2-0675665e201b")),
        )
    }
    edge_displays = {
        (CodeExecutionNode.Ports.default, MapNode): EdgeDisplay(id=UUID("c1ed7a7c-b278-4a4e-a8d0-53366bfa4a3d")),
        (MapNode.Ports.default, FinalOutput): EdgeDisplay(id=UUID("2e2e5cdc-94be-4df2-9e00-23467e2ea209")),
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("d9269719-a7a2-4388-9b85-73e329a78d16"), name="final-output"
        )
    }
