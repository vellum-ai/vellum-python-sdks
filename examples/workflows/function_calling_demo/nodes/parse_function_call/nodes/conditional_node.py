from vellum.workflows.nodes.displayable import ConditionalNode
from vellum.workflows.ports import Port

from .parse_function_call import ParseFunctionCall1


class ConditionalNode1(ConditionalNode):
    class Ports(ConditionalNode.Ports):
        branch_1 = Port.on_if(ParseFunctionCall1.Outputs.error.is_not_nil())
        branch_2 = Port.on_else()
