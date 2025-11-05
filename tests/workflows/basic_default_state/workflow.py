from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    example: str = "hello"


class State(BaseState):
    example: int = 5


class StartNode(BaseNode):
    example_input = Inputs.example
    example_state = State.example

    class Outputs(BaseOutputs):
        example_input: str
        example_state: int

    def run(self) -> Outputs:
        return self.Outputs(
            example_input=self.example_input,
            example_state=self.example_state,
        )


class BasicDefaultStateWorkflow(BaseWorkflow[Inputs, State]):
    graph = StartNode

    class Outputs(BaseOutputs):
        example_input = StartNode.Outputs.example_input
        example_state = StartNode.Outputs.example_state
