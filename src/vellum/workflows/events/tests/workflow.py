"""Simple workflow for testing monitoring decorators - Production-style setup."""

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
    item = MapNode.SubworkflowInputs.item
    index = MapNode.SubworkflowInputs.index

    class Outputs(BaseOutputs):
        count: int

    def run(self) -> Outputs:
        return self.Outputs(count=len(self.item) + self.index)


class IterationSubworkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
    graph = Iteration
    _enable_monitoring = True

    class Outputs(BaseOutputs):
        count = Iteration.Outputs.count


class MapFruitsNode(MapNode):
    items = Inputs.fruits
    subworkflow = IterationSubworkflow


class SimpleMapExample(BaseWorkflow[Inputs, BaseState]):
    _enable_monitoring = True
    graph = MapFruitsNode

    class Outputs(BaseOutputs):
        final_value = MapFruitsNode.Outputs.count
