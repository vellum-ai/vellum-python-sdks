from vellum.workflows.nodes.displayable import ConditionalNode
from vellum.workflows.ports import Port

from .has_function_calls import HasFunctionCalls


class ShouldHandleFunctions(ConditionalNode):
    class Ports(ConditionalNode.Ports):
        branch_1 = Port.on_if(HasFunctionCalls.Outputs.result.equals("True"))
        branch_2 = Port.on_else()
