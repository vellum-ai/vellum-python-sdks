from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState
from vellum.workflows.types.core import Json

from ..inputs import Inputs
from .invoke_function_s_w_code import InvokeFunctionSWCode


class FunctionResultContext(TemplatingNode[BaseState, Json]):
    template = """\
{
  \"function_context\": {
    \"name\": \"{{ item.value.name }}\",
    \"tool_id\": \"{{ item.value.id }}\",
    \"args\": {{ item.value.arguments | tojson }}
  },
  \"function_result\": {{ fxn_result | tojson }}
}\
"""
    inputs = {
        "item": Inputs.item,
        "fxn_result": InvokeFunctionSWCode.Outputs.result,
    }
