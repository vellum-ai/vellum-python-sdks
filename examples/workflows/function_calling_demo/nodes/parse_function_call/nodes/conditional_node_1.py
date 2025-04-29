from vellum.workflows.nodes.displayable import ConditionalNode
from vellum.workflows.ports import Port

from .is_valid_function_name import IsValidFunctionName


class ConditionalNode2(ConditionalNode):
    class Ports(ConditionalNode.Ports):
        branch_1 = Port.on_if(IsValidFunctionName.Outputs.result.equals("True"))
        branch_2 = Port.on_else()
