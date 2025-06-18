from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    input_value: str


class State(BaseState):
    state_value: str


class StartNode(BaseNode):
    input_value = Inputs.input_value
    state_value = State.state_value

    class Outputs(BaseNode.Outputs):
        input_value: str
        state_value: str

    def run(self) -> Outputs:
        return self.Outputs(input_value=self.input_value, state_value=self.state_value)


class MiddleNode(BaseNode):
    class ExternalInputs(BaseNode.ExternalInputs):
        message: str


class EndNode(BaseNode):
    start_input = StartNode.Outputs.input_value
    start_state = StartNode.Outputs.state_value
    middle_message = MiddleNode.ExternalInputs.message

    class Outputs(BaseNode.Outputs):
        final_value: str

    def run(self) -> Outputs:
        return self.Outputs(final_value=f"{self.start_input} {self.middle_message} {self.start_state}")


class BasicInputNodeWorkflow(BaseWorkflow[Inputs, State]):
    graph = StartNode >> MiddleNode >> EndNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = EndNode.Outputs.final_value
