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

from ....nodes.parse_function_call.nodes.allowed_function_names import AllowedFunctionNames
from ....nodes.parse_function_call.nodes.args import Args
from ....nodes.parse_function_call.nodes.conditional_node_1 import ConditionalNode2
from ....nodes.parse_function_call.nodes.error_message import ErrorMessage
from ....nodes.parse_function_call.nodes.error_node import ErrorNode1
from ....nodes.parse_function_call.nodes.is_valid_function_name import IsValidFunctionName
from ....nodes.parse_function_call.nodes.merge_node import MergeNode
from ....nodes.parse_function_call.nodes.name import Name
from ....nodes.parse_function_call.nodes.parse_function_args import ParseFunctionArgs
from ....nodes.parse_function_call.nodes.parse_function_call import ParseFunctionCall1
from ....nodes.parse_function_call.nodes.parse_function_name import ParseFunctionName
from ....nodes.parse_function_call.nodes.parse_tool_id import ParseToolID
from ....nodes.parse_function_call.nodes.tool_id import ToolID
from ....nodes.parse_function_call.workflow import ParseFunctionCallWorkflow


class ParseFunctionCallWorkflowDisplay(BaseWorkflowDisplay[ParseFunctionCallWorkflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("b0a312c5-c07e-4ba8-b434-575646ca8320"),
        entrypoint_node_source_handle_id=UUID("be47c6ac-495c-498d-b318-f479c02c687a"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1170, y=585), width=None, height=None),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-76.39160156249994, y=147.875, zoom=0.25)
        ),
    )
    inputs_display = {}
    entrypoint_displays = {
        ParseFunctionCall1: EntrypointDisplay(
            id=UUID("b0a312c5-c07e-4ba8-b434-575646ca8320"),
            edge_display=EdgeDisplay(id=UUID("d4104764-f0ce-4c79-86d0-9dbca9dc3e9e")),
        )
    }
    edge_displays = {
        (ParseFunctionCall1.Ports.default, ParseFunctionName): EdgeDisplay(
            id=UUID("3c8a7288-2816-413b-a835-e9576dceb3c6")
        ),
        (ParseFunctionCall1.Ports.default, ParseFunctionArgs): EdgeDisplay(
            id=UUID("e1f8cc9d-8991-497a-ae85-c9b0addf79f7")
        ),
        (ParseFunctionName.Ports.default, MergeNode): EdgeDisplay(id=UUID("21b5c3b3-6b17-49d2-8042-d9ed0b5fc2b6")),
        (ParseFunctionArgs.Ports.default, MergeNode): EdgeDisplay(id=UUID("73fd983e-ec53-4b8a-bb6e-bd4284450a12")),
        (MergeNode.Ports.default, IsValidFunctionName): EdgeDisplay(id=UUID("269aed35-de3f-4d49-af39-534c7e69b404")),
        (ParseFunctionCall1.Ports.default, AllowedFunctionNames): EdgeDisplay(
            id=UUID("be74615e-f7e9-4467-a9de-b612975a6f9d")
        ),
        (IsValidFunctionName.Ports.default, ConditionalNode2): EdgeDisplay(
            id=UUID("fc6f2bb0-3287-4a37-895f-840f7eacb31c")
        ),
        (ConditionalNode2.Ports.branch_1, Name): EdgeDisplay(id=UUID("55c22812-f470-4ea9-8509-89d398df8ce7")),
        (ConditionalNode2.Ports.branch_2, ErrorMessage): EdgeDisplay(id=UUID("3c890c21-4e40-4b11-8e68-8663609bc622")),
        (ErrorMessage.Ports.default, ErrorNode1): EdgeDisplay(id=UUID("5eecd64f-68e4-4695-8977-2cd78874a129")),
        (ConditionalNode2.Ports.branch_1, Args): EdgeDisplay(id=UUID("57778d49-b44c-4c62-9198-c848b20c4d4f")),
        (ParseFunctionCall1.Ports.default, ParseToolID): EdgeDisplay(id=UUID("be6cc434-ab29-4cfb-aef3-6815bee41acf")),
        (ParseToolID.Ports.default, MergeNode): EdgeDisplay(id=UUID("0074731f-548f-4ba0-bdc8-a024c9aef5fb")),
        (AllowedFunctionNames.Ports.default, MergeNode): EdgeDisplay(id=UUID("37a1b5b8-9c33-47fb-a3a3-4c5eae1247a8")),
        (ConditionalNode2.Ports.branch_1, ToolID): EdgeDisplay(id=UUID("51ab1ee1-57d6-4d18-bdb0-c3dc85e40a71")),
    }
    output_displays = {
        ParseFunctionCallWorkflow.Outputs.function_args: WorkflowOutputDisplay(
            id=UUID("d520f0a1-c28f-4007-acf9-2758871f2250"), name="function-args"
        ),
        ParseFunctionCallWorkflow.Outputs.function_name: WorkflowOutputDisplay(
            id=UUID("680f2d8d-b03a-43b9-9d77-626044e03227"), name="function-name"
        ),
        ParseFunctionCallWorkflow.Outputs.tool_id: WorkflowOutputDisplay(
            id=UUID("764c26a4-b0c4-4a52-9e19-96e651eccbd3"), name="tool-id"
        ),
    }
