from vellum.workflows.nodes.displayable import ConditionalNode as BaseConditionalNode
from vellum.workflows.ports import Port

from .templating_node import TemplatingNode


class ConditionalNode(BaseConditionalNode):
    class Ports(BaseConditionalNode.Ports):
        if_1 = Port.on_if(TemplatingNode.Outputs.result.does_not_equal("hello!"))
        else_1 = Port.on_else()
