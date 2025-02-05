from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports.port import Port

from tests.workflows.await_all_executions.workflow import SecondNode


class LoopNode(BaseNode):
    class Ports(BaseNode.Ports):
        loop = Port.on_if(SecondNode.Execution.count.less_than(2))
