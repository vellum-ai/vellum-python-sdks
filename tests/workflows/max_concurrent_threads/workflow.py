import time

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class State(BaseState):
    value = 1


class TopNode(BaseNode[State]):
    def run(self) -> BaseNode.Outputs:
        time.sleep(0.1)
        return self.Outputs()


class MiddleNode(BaseNode[State]):
    def run(self) -> BaseNode.Outputs:
        time.sleep(0.1)
        return self.Outputs()


class BottomNode(BaseNode[State]):
    def run(self) -> BaseNode.Outputs:
        time.sleep(0.1)
        return self.Outputs()


class MaxConcurrentThreadsExample(BaseWorkflow[BaseInputs, State]):
    """
    This workflow demonstrates how we get a different result when we run the workflow in serial
    vs. parallel, using the `concurrency` parameter.
    """

    graph = {
        TopNode,
        MiddleNode,
        BottomNode,
    }

    class Outputs(BaseOutputs):
        final_value = State.value
