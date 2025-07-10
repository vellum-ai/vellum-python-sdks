from typing import List

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state.base import BaseState


class Inputs(BaseInputs):
    message: str


class State(BaseState):
    messages: List[str] = []


class StateWritingNode(BaseNode[State]):
    message = Inputs.message

    def run(self) -> BaseNode.Outputs:
        for i in range(3):
            new_message = f"{self.message} - write {i + 1}"
            self.state.messages.append(new_message)

        return self.Outputs()


class StateArrayStreamingWorkflow(BaseWorkflow[Inputs, State]):
    graph = StateWritingNode

    class Outputs(BaseOutputs):
        final_messages = State.messages
