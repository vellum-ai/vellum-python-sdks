import random

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs


class StartNode(BaseNode):
    class Outputs(BaseOutputs):
        next_value: int

    def run(self) -> Outputs:
        return self.Outputs(next_value=random.randint(0, 100))


class TrivialWorkflow(BaseWorkflow):
    graph = StartNode
