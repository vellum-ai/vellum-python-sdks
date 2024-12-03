import time
from typing import Iterable, Iterator, List, Set

from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode
from vellum.workflows.outputs import BaseOutput
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.ports.port import Port
from vellum.workflows.state import BaseState
from vellum.workflows.workflows import BaseWorkflow


class Inputs(BaseInputs):
    fruits: List[str]


class State(BaseState):
    outputs: List[str] = []


class FirstNode(BaseNode[State]):
    fruits = Inputs.fruits

    class Outputs(BaseNode.Outputs):
        reversed: List[str]

    class Ports(BaseNode.Ports):
        default = Port(default=True)

        def __call__(self, outputs: BaseOutputs, state: BaseState) -> Set[Port]:
            return set()

        def __lt__(self, output: BaseOutput) -> Set[Port]:
            if output.is_initiated:
                return {self.default}

            return set()

    def run(self) -> Iterator[BaseOutput]:
        reversed_fruits = []
        for index, fruit in enumerate(self.fruits):
            time.sleep(0.01 * (index + 1))
            reversed = fruit[::-1]
            self.state.outputs.append(reversed)
            reversed_fruits.append(reversed)
            yield BaseOutput(delta=reversed, name="reversed")

        yield BaseOutput(value=reversed_fruits, name="reversed")


class SecondNode(BaseNode[State]):
    items = FirstNode.Outputs.reversed

    class Outputs(BaseNode.Outputs):
        doubled: List[str]

    def run(self) -> Iterator[BaseOutput]:
        doubled_fruits = []
        for index, item in enumerate(self.items):
            time.sleep(0.01 * (index + 1))
            doubled = item + " " + item
            self.state.outputs.append(doubled)
            doubled_fruits.append(doubled)
            yield BaseOutput(delta=doubled, name="doubled")

        yield BaseOutput(value=doubled_fruits, name="doubled")


class StreamingNodePipelineWorkflow(BaseWorkflow[Inputs, State]):
    """
    This workflow ensures that we support the pipelining of streaming node outputs from one node to the next.

    We prove this out with a simple pipeline of two streaming nodes, appending their outputs to the same
    state to ensure invocation order.
    """

    graph = FirstNode >> SecondNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = SecondNode.Outputs.doubled
        final_state = State.outputs
