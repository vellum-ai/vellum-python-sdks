from typing import List, Optional

from vellum import ChatMessage
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    message: str


class State(BaseState):
    chat_history: Optional[List[ChatMessage]] = []


class StartNode(BaseNode):
    class Outputs(BaseOutputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="executed")


class MutableDefaultStateWorkflow(BaseWorkflow[Inputs, State]):
    graph = StartNode

    class Outputs(BaseOutputs):
        final_result = StartNode.Outputs.result
