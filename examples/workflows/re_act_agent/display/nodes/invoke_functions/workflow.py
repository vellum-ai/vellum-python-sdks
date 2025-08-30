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

from ....nodes.invoke_functions.inputs import Inputs
from ....nodes.invoke_functions.nodes.final_output import FinalOutput
from ....nodes.invoke_functions.nodes.function_result_context import FunctionResultContext
from ....nodes.invoke_functions.nodes.invoke_function_s_w_code import InvokeFunctionSWCode
from ....nodes.invoke_functions.workflow import InvokeFunctionsWorkflow


class InvokeFunctionsWorkflowDisplay(BaseWorkflowDisplay[InvokeFunctionsWorkflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("82475913-3e24-4995-aa56-275cd8264944"),
        entrypoint_node_source_handle_id=UUID("5790a065-973f-4482-8cba-7f2ae7b91d29"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=178, y=223.5), width=None, height=None),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-10.090909090909065, y=177.69981471260743, zoom=0.39383426634077107)
        ),
    )
    inputs_display = {
        Inputs.index: WorkflowInputsDisplay(id=UUID("5e23c5c2-077b-4fe9-b223-9f3d3d374057"), name="index"),
        Inputs.items: WorkflowInputsDisplay(id=UUID("98ee5b96-8446-4cd6-90c7-2141432ff0b6"), name="items"),
        Inputs.item: WorkflowInputsDisplay(id=UUID("81372cd4-6664-4144-9b80-e5fd86ab2960"), name="item"),
    }
    entrypoint_displays = {
        InvokeFunctionSWCode: EntrypointDisplay(
            id=UUID("82475913-3e24-4995-aa56-275cd8264944"),
            edge_display=EdgeDisplay(id=UUID("bd2edba7-4191-4380-b5f5-8fe0c37e6112")),
        )
    }
    edge_displays = {
        (InvokeFunctionSWCode.Ports.default, FunctionResultContext): EdgeDisplay(
            id=UUID("54d7ea45-8951-47fd-958e-f3af0d5c98f6")
        ),
        (FunctionResultContext.Ports.default, FinalOutput): EdgeDisplay(
            id=UUID("d197a876-184d-4838-98f5-badfc537272d")
        ),
    }
    output_displays = {
        InvokeFunctionsWorkflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("fe14414b-f4de-4f26-9339-63e3fab65ce8"), name="final-output"
        )
    }
