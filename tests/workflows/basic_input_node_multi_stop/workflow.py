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


class TransitionNode(BaseNode):
    start_input = StartNode.Outputs.input_value
    middle_message = MiddleNode.ExternalInputs.message

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result=f"{self.start_input} {self.middle_message}")


class MiddleNode2(BaseNode):
    class ExternalInputs(BaseNode.ExternalInputs):
        message: str


class EndNode(BaseNode):
    start_input = StartNode.Outputs.input_value
    start_state = StartNode.Outputs.state_value
    middle_message = MiddleNode.ExternalInputs.message
    middle_message2 = MiddleNode2.ExternalInputs.message

    class Outputs(BaseNode.Outputs):
        final_value: str

    def run(self) -> Outputs:
        return self.Outputs(
            final_value=f"{self.start_input} {self.middle_message} {self.middle_message2} {self.start_state}"
        )


class BasicInputNodeWorkflow(BaseWorkflow[Inputs, State]):
    """
    This Workflow has two nodes that accept `ExternalInputs` of the same shape to ensure that they
    could each receive external data separately.
    """

    graph = StartNode >> MiddleNode >> TransitionNode >> MiddleNode2 >> EndNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = EndNode.Outputs.final_value
