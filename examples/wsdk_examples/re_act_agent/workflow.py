from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.accumulate_chat_history import AccumulateChatHistory
from .nodes.agent_node import AgentNode
from .nodes.agent_response import AgentResponse
from .nodes.final_accumulation_of_chat_history import FinalAccumulationOfChatHistory
from .nodes.full_chat_history_output import FullChatHistoryOutput
from .nodes.function_calls_to_json_array import FunctionCallsToJSONArray
from .nodes.has_function_calls import HasFunctionCalls
from .nodes.invoke_functions import InvokeFunctions
from .nodes.should_handle_functions import ShouldHandleFunctions


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = (
        AgentNode
        >> HasFunctionCalls
        >> {
            ShouldHandleFunctions.Ports.branch_1
            >> FunctionCallsToJSONArray
            >> InvokeFunctions
            >> AccumulateChatHistory
            >> AgentNode,
            ShouldHandleFunctions.Ports.branch_2
            >> FinalAccumulationOfChatHistory
            >> {
                FullChatHistoryOutput,
                AgentResponse,
            },
        }
    )

    class Outputs(BaseWorkflow.Outputs):
        response = AgentResponse.Outputs.value
        full_chat_history = FullChatHistoryOutput.Outputs.value
