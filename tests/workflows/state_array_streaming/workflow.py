from typing import Iterator, List

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutput, BaseOutputs
from vellum.workflows.state.base import BaseState


class Inputs(BaseInputs):
    message: str


class State(BaseState):
    messages: List[str] = []


class StateWritingNode(BaseNode[State]):
    message = Inputs.message

    class Outputs(BaseOutputs):
        final_messages: List[str]

    def run(self) -> Iterator[BaseOutput]:
        for i in range(3):
            new_message = f"{self.message} - write {i + 1}"
            self.state.messages.append(new_message)
            yield BaseOutput(name="final_messages", delta=new_message)

        return self.Outputs(final_messages=self.state.messages)


class StateArrayStreamingWorkflow(BaseWorkflow[Inputs, State]):
    graph = StateWritingNode

    class Outputs(BaseOutputs):
        final_messages = State.messages
