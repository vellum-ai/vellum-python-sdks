import time

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.core import MergeBehavior


class State(BaseState):
    counter = 0


class StartNode(BaseNode):
    pass


class TopNode(BaseNode):
    counter = State.counter

    class Outputs(BaseNode.Outputs):
        value = "hello"

    def run(self) -> Outputs:
        if self.counter >= 1:
            time.sleep(0.03)

        return self.Outputs()


class BottomNode(BaseNode):
    counter = State.counter

    class Outputs(BaseNode.Outputs):
        value = "world"

    def run(self) -> Outputs:
        if self.counter < 1:
            time.sleep(0.02)

        return self.Outputs()


class LoopNode(BaseNode[State]):
    class Ports(BaseNode.Ports):
        loop = Port.on_if(State.counter.less_than(2))
        end = Port.on_else()

    class Outputs(BaseNode.Outputs):
        value = TopNode.Outputs.value.coalesce(BottomNode.Outputs.value)

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    def run(self) -> BaseNode.Outputs:
        self.state.counter += 1
        return self.Outputs()


class EndNode(BaseNode):
    pass


class MiddleNode(BaseNode):
    pass


class MiddleNode2(BaseNode):
    pass


class MultiBranchMergeLoopMultiLengthWorkflow(BaseWorkflow[BaseInputs, State]):
    """
    This workflow is similar to the MultiBranchMergeLoopWorkflow, but the loop
    has a different length.
    """

    graph = (
        StartNode
        >> {
            TopNode >> MiddleNode,
            BottomNode >> MiddleNode2,
        }
        >> {
            LoopNode.Ports.loop >> StartNode,
            LoopNode.Ports.end >> EndNode,
        }
    )

    class Outputs(BaseWorkflow.Outputs):
        final_value = LoopNode.Outputs.value
        final_counter = State.counter
