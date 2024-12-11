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
from ..nodes.final_output import FinalOutput
from ..nodes.guardrail_node import GuardrailNode
from ..workflow import Workflow


class WorkflowDisplay(VellumWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaVellumDisplayOverrides(
        entrypoint_node_id=UUID("872c757c-9544-4ad6-ada5-5ee574f1fe5e"),
        entrypoint_node_source_handle_id=UUID("5751330f-60a8-4d6a-88aa-a35b968db364"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-864.6595419012735, y=161.5850325261029, zoom=0.59148308095993)
        ),
    )
    inputs_display = {
        Inputs.expected: WorkflowInputsVellumDisplayOverrides(
            id=UUID("a6ef8809-346e-469c-beed-2e5c4e9844c5"), required=True
        ),
        Inputs.actual: WorkflowInputsVellumDisplayOverrides(
            id=UUID("1472503c-1662-4da9-beb9-73026be90c68"), required=True
        ),
    }
    entrypoint_displays = {
        GuardrailNode: EntrypointVellumDisplayOverrides(
            id=UUID("872c757c-9544-4ad6-ada5-5ee574f1fe5e"),
            edge_display=EdgeVellumDisplayOverrides(id=UUID("26e54d68-9d79-4551-87a4-b4e0a3dd000e")),
        )
    }
    edge_displays = {
        (GuardrailNode.Ports.default, FinalOutput): EdgeVellumDisplayOverrides(
            id=UUID("cfda52fa-313b-4aa4-b673-28b74ed5f290")
        )
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputVellumDisplayOverrides(
            id=UUID("493cfa4b-5235-4b71-99ef-270955f35fcb"),
            node_id=UUID("a9455dc7-85f5-43a9-8be7-f131bc5f08e2"),
            node_input_id=UUID("ff856e07-ed9a-47fa-8cec-76ebd8795cdb"),
            name="final-output",
            label="Final Output",
            target_handle_id=UUID("0ef13a41-8905-45ad-9aee-09c201368981"),
            display_data=NodeDisplayData(position=NodeDisplayPosition(x=2750, y=210), width=458, height=234),
            edge_id=UUID("cfda52fa-313b-4aa4-b673-28b74ed5f290"),
        )
    }
