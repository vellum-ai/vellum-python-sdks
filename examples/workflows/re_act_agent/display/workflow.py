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
from ..nodes.accumulate_chat_history import AccumulateChatHistory
from ..nodes.agent_node import AgentNode
from ..nodes.agent_response import AgentResponse
from ..nodes.final_accumulation_of_chat_history import FinalAccumulationOfChatHistory
from ..nodes.full_chat_history_output import FullChatHistoryOutput
from ..nodes.function_calls_to_json_array import FunctionCallsToJSONArray
from ..nodes.has_function_calls import HasFunctionCalls
from ..nodes.invoke_functions import InvokeFunctions
from ..nodes.should_handle_functions import ShouldHandleFunctions
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("1f17313d-882b-447a-abdc-fb44968e3a6f"),
        entrypoint_node_source_handle_id=UUID("42f599f4-63c2-4f3b-982e-85e52b87abb0"),
        entrypoint_node_display=NodeDisplayData(
            position=NodeDisplayPosition(x=203.46768560224905, y=352.2267925183055), width=124, height=48
        ),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-68.83924799891861, y=141.87308637345325, zoom=0.256956455896284)
        ),
    )
    inputs_display = {
        Inputs.chat_history: WorkflowInputsDisplay(id=UUID("5485250c-9067-4ae0-aa02-223202b026a8"), name="chat_history")
    }
    entrypoint_displays = {
        AgentNode: EntrypointDisplay(
            id=UUID("1f17313d-882b-447a-abdc-fb44968e3a6f"),
            edge_display=EdgeDisplay(id=UUID("5a761d62-9de2-4781-a5d5-de9ef52d91ed")),
        )
    }
    edge_displays = {
        (AgentNode.Ports.default, HasFunctionCalls): EdgeDisplay(id=UUID("0ee48898-c59e-4a76-a854-4075b89f8e01")),
        (HasFunctionCalls.Ports.default, ShouldHandleFunctions): EdgeDisplay(
            id=UUID("7f2c620f-a2d3-4de8-88c5-4ce6ad5206fd")
        ),
        (ShouldHandleFunctions.Ports.branch_2, FinalAccumulationOfChatHistory): EdgeDisplay(
            id=UUID("41be00b4-1050-48f4-83a1-3fce04c28339")
        ),
        (FinalAccumulationOfChatHistory.Ports.default, FullChatHistoryOutput): EdgeDisplay(
            id=UUID("5929d6b5-9501-48a4-a26e-4ae4ccb23beb")
        ),
        (ShouldHandleFunctions.Ports.branch_1, FunctionCallsToJSONArray): EdgeDisplay(
            id=UUID("cf02f0b9-b3f2-4ae1-a2f3-fc2e4c47b832")
        ),
        (AccumulateChatHistory.Ports.default, AgentNode): EdgeDisplay(id=UUID("c0f0755d-8b60-4013-9e8d-521219fb772d")),
        (FinalAccumulationOfChatHistory.Ports.default, AgentResponse): EdgeDisplay(
            id=UUID("aab8fac8-f801-4e8e-9d8b-c764f7a35843")
        ),
        (FunctionCallsToJSONArray.Ports.default, InvokeFunctions): EdgeDisplay(
            id=UUID("4738ecfb-964a-4d7f-8ba9-0b1e1cbced28")
        ),
        (InvokeFunctions.Ports.default, AccumulateChatHistory): EdgeDisplay(
            id=UUID("62722b88-b459-44fd-b3a0-eaa13a9b4683")
        ),
    }
    output_displays = {
        Workflow.Outputs.response: WorkflowOutputDisplay(
            id=UUID("23f727b7-d00e-48df-8387-f1ea21e1bcb6"), name="response"
        ),
        Workflow.Outputs.full_chat_history: WorkflowOutputDisplay(
            id=UUID("b6effd4f-662d-4cae-9847-9598f3898660"), name="full-chat-history"
        ),
    }
