from typing import List

from vellum import ChatMessage
from vellum.workflows.nodes.displayable import CodeExecutionNode
from vellum.workflows.references import LazyReference
from vellum.workflows.state import BaseState

from ...inputs import Inputs
from ..invoke_functions import InvokeFunctions


class AccumulateChatHistory(CodeExecutionNode[BaseState, List[ChatMessage]]):
    filepath = "./script.py"
    code_inputs = {
        "invoked_functions": InvokeFunctions.Outputs.final_output,
        "assistant_message": LazyReference("AgentNode.Outputs.results"),
        "current_chat_history": LazyReference(
            lambda: AccumulateChatHistory.Outputs.result.coalesce(Inputs.chat_history)
        ),
    }
    runtime = "PYTHON_3_11_6"
    packages = []
