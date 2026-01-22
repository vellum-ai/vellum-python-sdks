from vellum.workflows.nodes.displayable import ConditionalNode as BaseConditionalNode
from vellum.workflows.ports import Port

from .templating_node import TemplatingNode


class ConditionalNode(BaseConditionalNode):
    class Ports(BaseConditionalNode.Ports):
        branch_1 = Port.on_if(TemplatingNode.Outputs.result.equals("weather"))
        branch_2 = Port.on_elif(TemplatingNode.Outputs.result.equals("flight status"))
        branch_3 = Port.on_elif(TemplatingNode.Outputs.result.equals("faa"))
        branch_4 = Port.on_else()

    class Display(BaseConditionalNode.Display):
        x = 2084.4413934539916
        y = 503.21512629358983
