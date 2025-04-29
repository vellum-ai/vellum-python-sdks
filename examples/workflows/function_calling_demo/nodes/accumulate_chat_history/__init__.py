from typing import List

from vellum import ChatMessage
from vellum.workflows.nodes.displayable import CodeExecutionNode
from vellum.workflows.references import LazyReference
from vellum.workflows.state import BaseState

from ...inputs import Inputs
from ..get_current_weather import GetCurrentWeather
from ..parse_function_call import ParseFunctionCall


class AccumulateChatHistory(CodeExecutionNode[BaseState, List[ChatMessage]]):
    filepath = "./script.py"
    code_inputs = {
        "tool_id": ParseFunctionCall.Outputs.tool_id,
        "function_result": GetCurrentWeather.Outputs.result,
        "assistant_message": LazyReference("PromptNode.Outputs.results"),
        "current_chat_history": Inputs.chat_history,
    }
    runtime = "PYTHON_3_11_6"
    packages = []
