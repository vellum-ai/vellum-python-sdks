from typing import List

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes import MapNode
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    items: List[int]


class State(BaseState):
    data: str = ""


class IterationNode(BaseNode):
    item = MapNode.SubworkflowInputs.item

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> Outputs:
        self.state.data += "x" * 1000  # 1KB per iteration
        return self.Outputs(result=self.state.data)


class IterationSubworkflow(BaseWorkflow[MapNode.SubworkflowInputs, State]):
    graph = IterationNode

    class Outputs(BaseOutputs):
        result = IterationNode.Outputs.result


class MapIterationsNode(MapNode):
    items = Inputs.items
    max_concurrency = 4
    subworkflow = IterationSubworkflow


class MapNodeStateGCWorkflow(BaseWorkflow[Inputs, State]):
    graph = MapIterationsNode

    class Outputs(BaseOutputs):
        results = MapIterationsNode.Outputs.result
