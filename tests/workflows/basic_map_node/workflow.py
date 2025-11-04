from typing import List

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes import MapNode
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    fruits: List[str]


class Iteration(BaseNode):
    __legacy_id__ = True
    item = MapNode.SubworkflowInputs.item
    index = MapNode.SubworkflowInputs.index

    class Outputs(BaseOutputs):
        count: int

    def run(self) -> Outputs:
        return self.Outputs(count=len(self.item) + self.index)


class IterationSubworkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
    graph = Iteration

    class Outputs(BaseOutputs):
        count = Iteration.Outputs.count


class MapFruitsNode(MapNode):
    items = Inputs.fruits
    subworkflow = IterationSubworkflow


class SimpleMapExample(BaseWorkflow[Inputs, BaseState]):
    graph = MapFruitsNode

    class Outputs(BaseOutputs):
        final_value = MapFruitsNode.Outputs.count
