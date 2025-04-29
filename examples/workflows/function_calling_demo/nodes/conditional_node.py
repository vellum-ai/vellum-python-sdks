from vellum.workflows.nodes.displayable import ConditionalNode as BaseConditionalNode
from vellum.workflows.ports import Port

from .parse_function_call import ParseFunctionCall


class ConditionalNode(BaseConditionalNode):
    class Ports(BaseConditionalNode.Ports):
        branch_1 = Port.on_if(ParseFunctionCall.Outputs.function_name.equals("get_current_weather"))
        branch_2 = Port.on_else()
