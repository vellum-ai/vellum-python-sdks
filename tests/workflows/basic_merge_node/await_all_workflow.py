from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.displayable.merge_node import MergeNode
from vellum.workflows.ports.port import Port
from vellum.workflows.references import LazyReference
from vellum.workflows.types.core import MergeBehavior
from vellum.workflows.workflows.base import BaseWorkflow


class StartNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value: str

    class Ports(BaseNode.Ports):
        first = Port.on_if(LazyReference(lambda: StartNode.Outputs.value.is_null()))
        second = Port.on_else()


class AwaitAllMergeNode(MergeNode):
    class Trigger(MergeNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ALL


class FirstPassthroughNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        pass

    def run(self) -> Outputs:
        return self.Outputs()


class SecondPassthroughNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        pass

    def run(self) -> Outputs:
        return self.Outputs()


class FinalPassthroughNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        return self.Outputs(value="output")


class AwaitAllPassingWorkflow(BaseWorkflow):
    graph = {FirstPassthroughNode, SecondPassthroughNode} >> AwaitAllMergeNode >> FinalPassthroughNode

    class Outputs(BaseWorkflow.Outputs):
        value = FinalPassthroughNode.Outputs.value


class AwaitAllFailingWorkflow(BaseWorkflow):
    graph = (
        {
            StartNode.Ports.first >> FirstPassthroughNode,
            StartNode.Ports.second >> SecondPassthroughNode,
        }
        >> AwaitAllMergeNode
        >> FinalPassthroughNode
    )

    class Outputs(BaseWorkflow.Outputs):
        value = FinalPassthroughNode.Outputs.value
