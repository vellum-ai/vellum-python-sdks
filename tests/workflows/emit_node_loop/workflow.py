from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    file_path: str


class State(BaseState):
    iteration: int = 0


class StartNode(BaseNode[State]):
    class Outputs(BaseNode.Outputs):
        iteration: int

    def run(self) -> BaseNode.Outputs:
        self.state.iteration += 1
        return self.Outputs(iteration=self.state.iteration)


class LoopNode(BaseNode[State]):
    class Ports(BaseNode.Ports):
        loop = Port.on_if(StartNode.Outputs.iteration.less_than(4), fork_state=True)
        end = Port.on_else()


class EmitNode(BaseNode[State]):
    external_data_source = Inputs.file_path
    iteration = State.iteration

    def run(self) -> BaseNode.Outputs:
        with open(self.external_data_source, "a") as f:
            f.write(f"Hello: {self.state.iteration}\n")

        return self.Outputs()


class EndNode(BaseNode[State]):
    class Outputs(BaseNode.Outputs):
        count = State.iteration


class EmitNodeLoopWorkflow(BaseWorkflow[Inputs, State]):
    """
    This workflow emits a message to a file 3 times. We want to
    ensure that each time the EmitNode is invoked, it's invoked with
    a its own copy (forked) of State.
    """

    graph = StartNode >> {
        LoopNode.Ports.loop >> StartNode,
        LoopNode.Ports.loop >> EmitNode,
        LoopNode.Ports.end >> EndNode,
    }

    class Outputs(BaseWorkflow.Outputs):
        count = State.iteration
        file_path = Inputs.file_path
