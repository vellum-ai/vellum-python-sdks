from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.references import LazyReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.core import MergeBehavior
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    condition: bool


class State(BaseState):
    pass


class BranchingNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        result: str

    class Ports(BaseNode.Ports):
        true_port = Port.on_if(LazyReference(lambda: Inputs.condition))
        false_port = Port.on_else()

    def run(self) -> Outputs:
        return self.Outputs(result="branched")


class TruePathNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        pass

    def run(self) -> Outputs:
        return self.Outputs()


class FalsePathNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        pass

    def run(self) -> Outputs:
        return self.Outputs()


class MergeNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        merged: str

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ALL

    def run(self) -> Outputs:
        return self.Outputs(merged="completed")


class FinalNode(BaseNode):
    merged = MergeNode.Outputs.merged

    class Outputs(BaseNode.Outputs):
        final: str

    def run(self) -> Outputs:
        return self.Outputs(final=self.merged)


class PortSplitAwaitAllWorkflow(BaseWorkflow[Inputs, State]):
    graph = (
        {
            BranchingNode.Ports.true_port >> TruePathNode,
            BranchingNode.Ports.false_port >> FalsePathNode,
        }
        >> MergeNode
        >> FinalNode
    )

    class Outputs(BaseWorkflow.Outputs):
        final = FinalNode.Outputs.final
