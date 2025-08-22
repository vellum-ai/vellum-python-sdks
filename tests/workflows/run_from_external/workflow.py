from datetime import datetime
import json
import os
import random
import tempfile
import threading
from uuid import UUID, uuid4
from typing import Iterator, Optional

from vellum.workflows.emitters.base import BaseWorkflowEmitter
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.events.node import NodeExecutionInitiatedBody, NodeExecutionInitiatedEvent
from vellum.workflows.events.workflow import WorkflowEvent
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.resolvers.base import BaseWorkflowResolver
from vellum.workflows.state.base import BaseState, StateMeta
from vellum.workflows.state.encoder import DefaultStateEncoder
from vellum.workflows.workflows.base import BaseWorkflow

mock_file_store = os.path.join(tempfile.gettempdir(), f"mock_store_{uuid4()}.json")
mock_file_lock = threading.Lock()


class MockFileEmitter(BaseWorkflowEmitter):
    def emit_event(self, event: WorkflowEvent) -> None:
        with mock_file_lock:
            if event.name == "workflow.execution.initiated":
                with open(mock_file_store, "w") as f:
                    json.dump({"events": [], "snapshots": []}, f)

            with open(mock_file_store) as f:
                content = f.read()
                data = json.loads(content)

            if event.name == "workflow.execution.initiated":
                # we only emit initiated node events bc this the only one that our resume logic currently needs
                # to reference and we're saving the rest until we have full json serialization support
                # https://app.shortcut.com/vellum/story/4786
                data["events"].append(event.model_dump())

            with open(mock_file_store, "w") as f:
                json.dump(data, f, cls=DefaultStateEncoder)

    def snapshot_state(self, state: BaseState) -> None:
        with mock_file_lock:
            with open(mock_file_store) as f:
                content = f.read()
                data = json.loads(content)

            data["snapshots"].append(state)
            with open(mock_file_store, "w") as f:
                json.dump(data, f, cls=DefaultStateEncoder)


class MockFileResolver(BaseWorkflowResolver):
    def get_latest_execution_events(self) -> Iterator[WorkflowEvent]:
        with mock_file_lock:
            with open(mock_file_store) as f:
                content = f.read()
                data = json.loads(content)

            for event in data["events"]:
                # we only emit initiated node events bc this the only one that our resume logic currently needs
                # to reference and we're saving the rest until we have full json serialization support
                # https://app.shortcut.com/vellum/story/4786
                if event["name"] == "node.execution.initiated":
                    yield NodeExecutionInitiatedEvent(
                        id=UUID(event["id"]),
                        timestamp=datetime.fromisoformat(event["ts"]),
                        trace_id=UUID(event["trace_id"]),
                        span_id=UUID(event["span_id"]),
                        body=NodeExecutionInitiatedBody(
                            node_definition=StartNode if event["node_definition"]["name"] == "StartNode" else NextNode,
                            inputs={},
                        ),
                    )

    def get_state_snapshot_history(self) -> Iterator[BaseState]:
        with mock_file_lock:
            with open(mock_file_store) as f:
                content = f.read()
                data = json.loads(content)

            for serialized_state in data["snapshots"]:
                meta = StateMeta.model_validate(serialized_state.pop("meta"))
                snapshot = BaseState(
                    **serialized_state,
                    meta=meta,
                )
                yield snapshot

    def load_state(self, previous_execution_id: Optional[UUID] = None) -> Optional[BaseState]:
        return None


class StartNode(BaseNode):
    class Outputs(BaseOutputs):
        next_value: int

    def run(self) -> Outputs:
        return self.Outputs(next_value=5)


class NextNode(BaseNode):
    next_value = StartNode.Outputs.next_value

    class Outputs(BaseOutputs):
        final_value: int

    def run(self) -> Outputs:
        delta = random.randint(0, 100)
        if delta > 95:
            raise NodeException("The next value is too high", code=WorkflowErrorCode.PROVIDER_ERROR)

        return self.Outputs(final_value=self.next_value + delta)


class RunFromExternalWorkflow(BaseWorkflow):
    graph = StartNode >> NextNode

    emitters = [MockFileEmitter()]
    resolvers = [MockFileResolver()]

    class Outputs(BaseOutputs):
        final_value = NextNode.Outputs.final_value
