from typing import List

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes import MapNode
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class Iteration(BaseNode[BaseState]):
    item: str = MapNode.SubworkflowInputs.item
    index = MapNode.SubworkflowInputs.index

    class Outputs(BaseOutputs):
        new_fruit: str

    def run(self) -> Outputs:
        new_fruit = self.item + " " + self.item
        parent_state = self.state.meta.parent
        if not isinstance(parent_state, State):
            raise ValueError("Parent state is wrong type")

        parent_state.new_fruits.append(new_fruit)
        return self.Outputs(new_fruit=new_fruit)


class IterationSubworkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
    graph = Iteration

    class Outputs(BaseOutputs):
        new_fruit = Iteration.Outputs.new_fruit


class Inputs(BaseInputs):
    fruits: List[str]


class State(BaseState):
    new_fruits: List[str] = []


class MapFruitsNode(MapNode):
    max_concurrency = 1
    items = Inputs.fruits
    subworkflow = IterationSubworkflow


class SerialMapExample(BaseWorkflow[Inputs, State]):
    """
    This workflow demonstrates how to use a Map Node with a max concurrency configuration.

    Because the inner node sleeps on the first item, it guarantees that state is only updated by
    the first element first if it's running in serial.
    """

    graph = MapFruitsNode

    class Outputs(BaseOutputs):
        final_value = State.new_fruits
