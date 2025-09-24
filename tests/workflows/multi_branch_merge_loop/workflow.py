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
        return self.Outputs()


class BottomNode(BaseNode):
    counter = State.counter

    class Outputs(BaseNode.Outputs):
        value = "world"

    def run(self) -> Outputs:
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


class MultiBranchMergeLoopWorkflow(BaseWorkflow[BaseInputs, State]):
    """
    This workflow runs in a loop twice, where the top branch executes
    the first time and the bottom branch executes the second time. This aims
    to verify two properties of workflow execution:
    - `LoopNode` is only executed twice in total, once for each iteration
    - `LoopNode.Outputs.value` is equal to the output of the _top_ branch in both
      iterations, since node outputs are immutable once executed.
    """

    graph = (
        StartNode
        >> {
            TopNode,
            BottomNode,
        }
        >> {
            LoopNode.Ports.loop >> StartNode,
            LoopNode.Ports.end >> EndNode,
        }
    )

    class Outputs(BaseWorkflow.Outputs):
        final_value = LoopNode.Outputs.value
        final_counter = State.counter
