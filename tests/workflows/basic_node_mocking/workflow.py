from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.workflows.base import BaseWorkflow


class StartNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        greeting: str

    def run(self) -> Outputs:
        raise NodeException("This node should be mocked")


class FinalNode(BaseNode):
    greeting = StartNode.Outputs.greeting

    class Outputs(BaseNode.Outputs):
        message: str

    def run(self) -> Outputs:
        return self.Outputs(message=f"{self.greeting}, World!")


class MockedNodeWorkflow(BaseWorkflow):
    graph = StartNode >> FinalNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = FinalNode.Outputs.message
