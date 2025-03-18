from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.types.core import MergeBehavior
from vellum.workflows.workflows.base import BaseWorkflow


class NodeA(BaseNode):
    class Outputs(BaseNode.Outputs):
        value = "A"


class NodeB(BaseNode):
    class Ports(BaseNode.Ports):
        loop = Port.on_if(NodeA.Execution.count.less_than(3))
        end = Port.on_else()

    class Outputs(BaseNode.Outputs):
        value = "B"


class NodeC(BaseNode):
    class Outputs(BaseNode.Outputs):
        value = "C"


class NodeD(BaseNode):
    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ALL

    a_count = NodeA.Execution.count
    b_count = NodeB.Execution.count
    c_count = NodeC.Execution.count

    class Outputs(BaseNode.Outputs):
        a_executions: int
        b_executions: int
        c_executions: int

    def run(self) -> Outputs:
        return self.Outputs(
            a_executions=self.a_count,
            b_executions=self.b_count,
            c_executions=self.c_count,
        )


class LoopBeforeAwaitAllWorkflow(BaseWorkflow):
    graph = {
        NodeA
        >> {
            NodeB.Ports.loop >> NodeA,  # loop this 3 times
            NodeB.Ports.end >> NodeD,  # `D` has AWAIT_ALL merge behavior
        },
        NodeC >> NodeD,
    }

    class Outputs(BaseWorkflow.Outputs):
        a_executions = NodeD.Outputs.a_executions
        b_executions = NodeD.Outputs.b_executions
        c_executions = NodeD.Outputs.c_executions
