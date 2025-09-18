import json
from typing import Iterator, List

from vellum.workflows import BaseWorkflow
from vellum.workflows.emitters import BaseWorkflowEmitter
from vellum.workflows.events import WorkflowEvent
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState
from vellum.workflows.state.encoder import DefaultStateEncoder
from vellum.workflows.types.core import JsonObject


class State(BaseState):
    score = 0


class StartNode(BaseNode):
    class Outputs(BaseOutputs):
        final_value: str

    def run(self) -> BaseOutputs:
        return self.Outputs(final_value="Hello, World!")


class NextNode(BaseNode[State]):
    start_node_output = StartNode.Outputs.final_value

    class Outputs(BaseOutputs):
        final_value: str

    def run(self) -> Outputs:
        self.state.score = len(self.start_node_output)
        return self.Outputs(final_value=f"Score: {self.state.score}")


class BasicEmitterWorkflow(BaseWorkflow[BaseInputs, State]):
    graph = StartNode >> NextNode

    class Outputs(BaseOutputs):
        final_value = NextNode.Outputs.final_value


class ExampleEmitter(BaseWorkflowEmitter):
    _events: List[WorkflowEvent] = []
    _state_snapshots: List[JsonObject] = []

    def emit_event(self, event: WorkflowEvent) -> None:
        self._events.append(event)

    def snapshot_state(self, state: BaseState) -> None:
        json_state = json.loads(json.dumps(state, cls=DefaultStateEncoder))
        self._state_snapshots.append(json_state)

    def join(self) -> None:
        pass

    @property
    def events(self) -> Iterator[WorkflowEvent]:
        return iter(self._events)

    @property
    def state_snapshots(self) -> Iterator[JsonObject]:
        return iter(self._state_snapshots)
