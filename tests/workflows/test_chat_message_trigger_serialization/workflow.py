from typing import List

from vellum import ChatMessage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state.base import BaseState

from .triggers.chat import Chat


class State(BaseState):
    chat_history: List[ChatMessage] = []


class SimpleNode(BaseNode):
    message = Chat.message

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> BaseOutputs:
        return self.Outputs(result=f"Received: {str(self.message)}")


class Workflow(BaseWorkflow[BaseInputs, State]):
    graph = Chat >> SimpleNode

    class Outputs(BaseOutputs):
        final_result = SimpleNode.Outputs.result
