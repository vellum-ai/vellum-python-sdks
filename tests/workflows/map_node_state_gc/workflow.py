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
    accumulated_data: List[str] = []


class IterationNode(BaseNode):
    item = MapNode.SubworkflowInputs.item
    index = MapNode.SubworkflowInputs.index

    class Outputs(BaseOutputs):
        result: str
        state_size: int

    def run(self) -> Outputs:
        large_string = f"iteration_{self.index}_" + ("x" * 1000)

        self.state.accumulated_data.append(large_string)

        return self.Outputs(result=large_string, state_size=len(self.state.accumulated_data))


class IterationSubworkflow(BaseWorkflow[MapNode.SubworkflowInputs, State]):
    graph = IterationNode

    class Outputs(BaseOutputs):
        result = IterationNode.Outputs.result
        state_size = IterationNode.Outputs.state_size


class MapIterationsNode(MapNode):
    items = Inputs.items
    max_concurrency = 4
    subworkflow = IterationSubworkflow


class MapNodeStateGCWorkflow(BaseWorkflow[Inputs, State]):
    graph = MapIterationsNode

    class Outputs(BaseOutputs):
        results = MapIterationsNode.Outputs.result
        state_sizes = MapIterationsNode.Outputs.state_size
