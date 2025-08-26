from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.resolvers.resolver import VellumResolver
from vellum.workflows.state.base import BaseState


class Inputs(BaseInputs):
    user_message: str


class State(BaseState):
    execution_count: int = 0


class CounterNode(BaseNode[State]):
    user_message = Inputs.user_message

    class Outputs(BaseOutputs):
        current_count: int
        user_message: str

    def run(self) -> Outputs:
        self.state.execution_count += 1
        return self.Outputs(current_count=self.state.execution_count, user_message=self.user_message)


class SpanLinkWorkflow(BaseWorkflow[Inputs, State]):
    graph = CounterNode
    resolvers = [VellumResolver()]

    class Outputs(BaseOutputs):
        current_count = CounterNode.Outputs.current_count
        user_message = CounterNode.Outputs.user_message
