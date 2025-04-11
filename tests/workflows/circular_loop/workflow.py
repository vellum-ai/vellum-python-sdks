from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.state.base import BaseState


class State(BaseState):
    counter: int = 0
    completed: bool = False


class TopNode(BaseNode[State]):
    class Outputs(BaseNode.Outputs):
        status: str

    def run(self) -> Outputs:
        if self.state.counter >= 2:
            self.state.completed = True
            return self.Outputs(status="complete")
        else:
            return self.Outputs(status="processing")


class BranchNode(BaseNode[State]):
    class Ports(BaseNode.Ports):
        branch_1 = Port.on_if(State.completed.equals(False))
        branch_complete = Port.on_else()


class IncrementCounterNode(BaseNode[State]):
    def run(self) -> BaseNode.Outputs:
        self.state.counter += 1
        return self.Outputs()


class IncompleteScrapeResultNode(BaseNode[State]):
    pass


class FinalOutputNode(BaseNode[State]):
    class Outputs(BaseNode.Outputs):
        counter: int
        completed: bool

    def run(self) -> "BaseNode.Outputs":
        return self.Outputs(counter=self.state.counter, completed=self.state.completed)


class StartNode(BaseNode[State]):
    pass


class CircularLoopWorkflow(BaseWorkflow[BaseInputs, State]):
    graph = (
        StartNode
        >> TopNode
        >> {
            BranchNode.Ports.branch_1 >> IncrementCounterNode >> TopNode,
            BranchNode.Ports.branch_complete >> FinalOutputNode,
        }
    )

    class Outputs(BaseWorkflow.Outputs):
        counter = FinalOutputNode.Outputs.counter
        completed = FinalOutputNode.Outputs.completed
