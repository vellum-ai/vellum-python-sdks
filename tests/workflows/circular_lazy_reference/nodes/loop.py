from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports.port import Port

from tests.workflows.circular_lazy_reference.nodes.second import SecondNode


class LoopNode(BaseNode):
    class Ports(BaseNode.Ports):
        loop = Port.on_if(SecondNode.Execution.count.less_than(2))
        else_branch = Port.on_else()
