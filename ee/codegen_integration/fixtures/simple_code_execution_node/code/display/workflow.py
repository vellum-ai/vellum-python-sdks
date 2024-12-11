from uuid import UUID

from vellum_ee.workflows.display.vellum import (
    EdgeVellumDisplayOverrides,
    EntrypointVellumDisplayOverrides,
    NodeDisplayData,
    NodeDisplayPosition,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowInputsVellumDisplayOverrides,
    WorkflowMetaVellumDisplayOverrides,
    WorkflowOutputVellumDisplayOverrides,
)
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay

from ..inputs import Inputs
from ..nodes.code_execution_node import CodeExecutionNode
from ..nodes.final_output import FinalOutput
from ..workflow import Workflow


class WorkflowDisplay(VellumWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaVellumDisplayOverrides(
        entrypoint_node_id=UUID("d49107fe-1424-42ba-9413-9ab5ce398077"),
        entrypoint_node_source_handle_id=UUID("08d78489-ce80-4743-a22d-2d5f62b575ac"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-1156.2121586299443, y=121.53015734265733, zoom=0.7888986013986014)
        ),
    )
    inputs_display = {
        Inputs.input: WorkflowInputsVellumDisplayOverrides(
            id=UUID("f55ef1d6-1d95-464c-adb1-11e3a19c2ed2"), required=True
        )
    }
    entrypoint_displays = {
        CodeExecutionNode: EntrypointVellumDisplayOverrides(
            id=UUID("d49107fe-1424-42ba-9413-9ab5ce398077"),
            edge_display=EdgeVellumDisplayOverrides(id=UUID("f9ff5d09-50a3-46bc-bca6-9f77886cc0e7")),
        )
    }
    edge_displays = {
        (CodeExecutionNode.Ports.default, FinalOutput): EdgeVellumDisplayOverrides(
            id=UUID("3936972b-ad88-4cc0-85a1-61b931ca3431")
        )
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputVellumDisplayOverrides(
            id=UUID("87760362-25b9-4dcb-8034-b49dc9e033ab"),
            node_id=UUID("5bb10d67-efc7-4bd4-9452-4ec2ffbc031d"),
            node_input_id=UUID("d3b9060a-40b5-492c-a628-f2d3c912cf44"),
            name="final-output",
            label="Final Output",
            target_handle_id=UUID("ab9dd41a-5c7b-484a-bcd5-d55658ea849c"),
            display_data=NodeDisplayData(
                position=NodeDisplayPosition(x=2392.5396121883655, y=235.35180055401668), width=480, height=234
            ),
            edge_id=UUID("3936972b-ad88-4cc0-85a1-61b931ca3431"),
        )
    }
