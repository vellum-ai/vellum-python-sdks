from typing import List

from vellum import ChatMessage
from vellum.workflows.nodes.displayable import CodeExecutionNode
from vellum.workflows.state import BaseState

from ...inputs import Inputs
from ..accumulate_chat_history import AccumulateChatHistory
from ..agent_node import AgentNode


class FinalAccumulationOfChatHistory(CodeExecutionNode[BaseState, List[ChatMessage]]):
    filepath = "./script.py"
    code_inputs = {
        "current_chat_history": AccumulateChatHistory.Outputs.result.coalesce(Inputs.chat_history),
        "assistant_message": AgentNode.Outputs.results,
    }
    runtime = "PYTHON_3_11_6"
    packages = []
