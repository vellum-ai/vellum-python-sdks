import pytest
from datetime import datetime, timezone
from uuid import UUID

from deepdiff import DeepDiff

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types import (
    NodeExecutionFulfilledEvent as ClientNodeExecutionFulfilledEvent,
    WorkflowExecutionFulfilledEvent as ClientWorkflowExecutionFulfilledEvent,
)
from vellum.workflows.constants import undefined
from vellum.workflows.errors.types import WorkflowError, WorkflowErrorCode
from vellum.workflows.events.exception_handling import stream_initialization_exception
from vellum.workflows.events.node import (
    NodeExecutionFulfilledBody,
    NodeExecutionFulfilledEvent,
    NodeExecutionInitiatedBody,
    NodeExecutionInitiatedEvent,
    NodeExecutionLogBody,
    NodeExecutionLogEvent,
    NodeExecutionStreamingBody,
    NodeExecutionStreamingEvent,
)
from vellum.workflows.events.types import NodeParentContext, ParentContext, WorkflowParentContext
from vellum.workflows.events.workflow import (
    WorkflowExecutionFulfilledBody,
    WorkflowExecutionFulfilledEvent,
    WorkflowExecutionInitiatedBody,
    WorkflowExecutionInitiatedEvent,
    WorkflowExecutionRejectedBody,
    WorkflowExecutionRejectedEvent,
    WorkflowExecutionStreamingBody,
    WorkflowExecutionStreamingEvent,
)
from vellum.workflows.exceptions import WorkflowInitializationException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.displayable.tool_calling_node.utils import ElseNode, RouterNode
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.core import VellumSecret
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum.workflows.workflows.base import BaseWorkflow
from vellum.workflows.workflows.event_filters import all_workflow_event_filter


class MockInputs(BaseInputs):
    foo: str


class MockNode(BaseNode):
    node_foo = MockInputs.foo
    node_secret = VellumSecretReference("secret")

    class Outputs(BaseNode.Outputs):
        example: str


class MockWorkflow(BaseWorkflow[MockInputs, BaseState]):
    graph = MockNode


name_parts = __name__.split(".")
module_root = name_parts[: name_parts.index("events")]
mock_workflow_uuid = str(uuid4_from_hash(MockWorkflow.__qualname__))
mock_node_uuid = str(MockNode.__id__)


@pytest.mark.parametrize(
    ["event", "expected_json"],
    [
        (
            WorkflowExecutionInitiatedEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                trace_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                body=WorkflowExecutionInitiatedBody(
                    workflow_definition=MockWorkflow,
                    inputs=MockInputs(foo="bar"),
                ),
            ),
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "api_version": "2024-10-25",
                "timestamp": "2024-01-01T12:00:00Z",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "workflow.execution.initiated",
                "body": {
                    "workflow_definition": {
                        "id": mock_workflow_uuid,
                        "name": "MockWorkflow",
                        "module": module_root + ["events", "tests", "test_event"],
                    },
                    "inputs": {
                        "foo": "bar",
                    },
                    "display_context": None,
                    "initial_state": None,
                    "workflow_version_exec_config": None,
                    "server_metadata": None,
                    "trigger": None,
                },
                "parent": None,
                "links": None,
            },
        ),
        (
            NodeExecutionInitiatedEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                trace_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                body=NodeExecutionInitiatedBody(
                    node_definition=MockNode,
                    inputs={
                        MockNode.node_foo: "bar",
                        MockNode.node_secret: VellumSecret(name="secret"),
                    },
                ),
                parent=NodeParentContext(
                    node_definition=MockNode,
                    span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                    parent=WorkflowParentContext(
                        workflow_definition=MockWorkflow,
                        span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                    ),
                ),
            ),
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "api_version": "2024-10-25",
                "timestamp": "2024-01-01T12:00:00Z",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "node.execution.initiated",
                "body": {
                    "node_definition": {
                        "id": mock_node_uuid,
                        "name": "MockNode",
                        "module": module_root + ["events", "tests", "test_event"],
                        "exclude_from_monitoring": False,
                    },
                    "inputs": {
                        "node_foo": "bar",
                        "node_secret": {
                            "name": "secret",
                        },
                    },
                },
                "parent": {
                    "node_definition": {
                        "id": mock_node_uuid,
                        "name": "MockNode",
                        "module": module_root + ["events", "tests", "test_event"],
                        "exclude_from_monitoring": False,
                    },
                    "parent": {
                        "workflow_definition": {
                            "id": mock_workflow_uuid,
                            "name": "MockWorkflow",
                            "module": module_root + ["events", "tests", "test_event"],
                        },
                        "type": "WORKFLOW",
                        "parent": None,
                        "span_id": "123e4567-e89b-12d3-a456-426614174000",
                    },
                    "type": "WORKFLOW_NODE",
                    "span_id": "123e4567-e89b-12d3-a456-426614174000",
                },
                "links": None,
            },
        ),
        (
            WorkflowExecutionStreamingEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                trace_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                body=WorkflowExecutionStreamingBody(
                    workflow_definition=MockWorkflow,
                    output=BaseOutput(
                        name="example",
                        value="foo",
                    ),
                ),
            ),
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "api_version": "2024-10-25",
                "timestamp": "2024-01-01T12:00:00Z",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "workflow.execution.streaming",
                "body": {
                    "workflow_definition": {
                        "id": mock_workflow_uuid,
                        "name": "MockWorkflow",
                        "module": module_root + ["events", "tests", "test_event"],
                    },
                    "output": {
                        "name": "example",
                        "value": "foo",
                    },
                },
                "parent": None,
                "links": None,
            },
        ),
        (
            WorkflowExecutionFulfilledEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                trace_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                body=WorkflowExecutionFulfilledBody(
                    workflow_definition=MockWorkflow,
                    outputs=MockNode.Outputs(
                        example="foo",
                    ),
                ),
            ),
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "api_version": "2024-10-25",
                "timestamp": "2024-01-01T12:00:00Z",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "workflow.execution.fulfilled",
                "body": {
                    "workflow_definition": {
                        "id": mock_workflow_uuid,
                        "name": "MockWorkflow",
                        "module": module_root + ["events", "tests", "test_event"],
                    },
                    "outputs": {
                        "example": "foo",
                    },
                    "final_state": None,
                    "server_metadata": None,
                },
                "parent": None,
                "links": None,
            },
        ),
        (
            WorkflowExecutionFulfilledEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                trace_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                body=WorkflowExecutionFulfilledBody(
                    workflow_definition=MockWorkflow,
                    outputs=MockNode.Outputs(
                        example="foo",
                    ),
                    final_state=BaseState(writable_value=42),
                ),
            ),
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "api_version": "2024-10-25",
                "timestamp": "2024-01-01T12:00:00Z",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "workflow.execution.fulfilled",
                "body": {
                    "workflow_definition": {
                        "id": mock_workflow_uuid,
                        "name": "MockWorkflow",
                        "module": module_root + ["events", "tests", "test_event"],
                    },
                    "outputs": {
                        "example": "foo",
                    },
                    "final_state": {
                        "writable_value": 42,
                    },
                    "server_metadata": None,
                },
                "parent": None,
                "links": None,
            },
        ),
        (
            WorkflowExecutionRejectedEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                trace_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                body=WorkflowExecutionRejectedBody(
                    workflow_definition=MockWorkflow,
                    error=WorkflowError(
                        message="Workflow failed",
                        code=WorkflowErrorCode.USER_DEFINED_ERROR,
                    ),
                ),
            ),
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "api_version": "2024-10-25",
                "timestamp": "2024-01-01T12:00:00Z",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "workflow.execution.rejected",
                "body": {
                    "workflow_definition": {
                        "id": mock_workflow_uuid,
                        "name": "MockWorkflow",
                        "module": module_root + ["events", "tests", "test_event"],
                    },
                    "error": {
                        "message": "Workflow failed",
                        "code": "USER_DEFINED_ERROR",
                        "raw_data": None,
                        "stacktrace": None,
                    },
                    "stacktrace": None,
                },
                "parent": None,
                "links": None,
            },
        ),
        (
            NodeExecutionStreamingEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                trace_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                body=NodeExecutionStreamingBody(
                    node_definition=MockNode,
                    output=BaseOutput(
                        name="example",
                        value="foo",
                    ),
                ),
            ),
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "api_version": "2024-10-25",
                "timestamp": "2024-01-01T12:00:00Z",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "node.execution.streaming",
                "body": {
                    "node_definition": {
                        "id": mock_node_uuid,
                        "name": "MockNode",
                        "module": module_root + ["events", "tests", "test_event"],
                        "exclude_from_monitoring": False,
                    },
                    "output": {
                        "name": "example",
                        "value": "foo",
                    },
                },
                "parent": None,
                "links": None,
            },
        ),
        (
            NodeExecutionFulfilledEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                trace_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                body=NodeExecutionFulfilledBody(
                    node_definition=MockNode,
                    outputs=MockNode.Outputs(
                        example="foo",
                    ),
                    invoked_ports={MockNode.Ports.default},
                ),
            ),
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "api_version": "2024-10-25",
                "timestamp": "2024-01-01T12:00:00Z",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "node.execution.fulfilled",
                "body": {
                    "node_definition": {
                        "id": mock_node_uuid,
                        "name": "MockNode",
                        "module": module_root + ["events", "tests", "test_event"],
                        "exclude_from_monitoring": False,
                    },
                    "outputs": {
                        "example": "foo",
                    },
                    "invoked_ports": [
                        {
                            "name": "default",
                        }
                    ],
                    "mocked": None,
                },
                "parent": None,
                "links": None,
            },
        ),
        (
            NodeExecutionFulfilledEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                trace_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                body=NodeExecutionFulfilledBody(
                    node_definition=MockNode,
                    outputs=MockNode.Outputs(
                        example=undefined,  # type: ignore[arg-type]
                    ),
                    invoked_ports={MockNode.Ports.default},
                ),
            ),
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "api_version": "2024-10-25",
                "timestamp": "2024-01-01T12:00:00Z",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "node.execution.fulfilled",
                "body": {
                    "node_definition": {
                        "id": mock_node_uuid,
                        "name": "MockNode",
                        "module": module_root + ["events", "tests", "test_event"],
                        "exclude_from_monitoring": False,
                    },
                    "outputs": {},
                    "invoked_ports": [
                        {
                            "name": "default",
                        }
                    ],
                    "mocked": None,
                },
                "parent": None,
                "links": None,
            },
        ),
        (
            NodeExecutionFulfilledEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                trace_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                body=NodeExecutionFulfilledBody(
                    node_definition=MockNode,
                    outputs=MockNode.Outputs(
                        example="foo",
                    ),
                    mocked=True,
                ),
            ),
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "api_version": "2024-10-25",
                "timestamp": "2024-01-01T12:00:00Z",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "node.execution.fulfilled",
                "body": {
                    "node_definition": {
                        "id": mock_node_uuid,
                        "name": "MockNode",
                        "module": module_root + ["events", "tests", "test_event"],
                        "exclude_from_monitoring": False,
                    },
                    "outputs": {"example": "foo"},
                    "mocked": True,
                },
                "parent": None,
                "links": None,
            },
        ),
        (
            NodeExecutionLogEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                trace_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                body=NodeExecutionLogBody(
                    node_definition=MockNode,
                    attributes={"foo": "bar"},
                    severity="INFO",
                    message="Test log message",
                ),
            ),
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "api_version": "2024-10-25",
                "timestamp": "2024-01-01T12:00:00Z",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "node.execution.log",
                "body": {
                    "node_definition": {
                        "id": mock_node_uuid,
                        "name": "MockNode",
                        "module": module_root + ["events", "tests", "test_event"],
                        "exclude_from_monitoring": False,
                    },
                    "attributes": {"foo": "bar"},
                    "severity": "INFO",
                    "message": "Test log message",
                },
                "parent": None,
                "links": None,
            },
        ),
    ],
    ids=[
        "workflow.execution.initiated",
        "node.execution.initiated",
        "workflow.execution.streaming",
        "workflow.execution.fulfilled",
        "workflow.execution.fulfilled_with_state",
        "workflow.execution.rejected",
        "node.execution.streaming",
        "node.execution.fulfilled",
        "fulfilled_node_with_undefined_outputs",
        "mocked_node",
        "node.execution.log",
    ],
)
def test_event_serialization(event, expected_json):
    assert not DeepDiff(event.model_dump(mode="json"), expected_json)


def test_parent_context__deserialize_from_json__invalid_parent_context():
    # GIVEN an event with a parent context that Vellum is introducing in the future
    data = {
        "foo": "bar",
        "parent": {
            "type": "SOME_FUTURE_ENTITY",
            "span_id": "123e4567-e89b-12d3-a456-426614174000",
            "some_randome_field": "some_random_value",
            "parent": None,
        },
    }

    # AND a dataclass that references the parent context
    class MyData(UniversalBaseModel):
        foo: str
        parent: ParentContext

    # WHEN the data is deserialized
    event = MyData.model_validate(data)

    # THEN the event is deserialized correctly
    assert event.parent
    assert event.parent.type == "UNKNOWN"
    assert event.parent.span_id == UUID("123e4567-e89b-12d3-a456-426614174000")
    assert event.parent.parent is None


def test_workflow_event_generator_stream_initialization_exception():
    """
    Tests that stream_initialization_exception yields both initiated and rejected events with proper correlation.
    """
    exception = WorkflowInitializationException("Test initialization error", workflow_definition=MockWorkflow)

    events = list(stream_initialization_exception(exception))

    assert len(events) == 2

    initiated_event = events[0]
    assert initiated_event.name == "workflow.execution.initiated"
    assert initiated_event.body.inputs is not None
    assert initiated_event.body.initial_state is None
    assert initiated_event.body.workflow_definition == MockWorkflow

    rejected_event = events[1]
    assert rejected_event.name == "workflow.execution.rejected"
    assert rejected_event.body.error.message == "Test initialization error"
    assert rejected_event.body.workflow_definition == MockWorkflow

    assert initiated_event.trace_id == rejected_event.trace_id
    assert initiated_event.span_id == rejected_event.span_id


def test_node_execution_initiated_event_includes_exclude_from_monitoring():
    """Test exclude_from_monitoring is included in node_definition when node has __exclude_from_monitoring__."""
    router_node_event = NodeExecutionInitiatedEvent(
        id=UUID("123e4567-e89b-12d3-a456-426614174001"),
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        trace_id=UUID("123e4567-e89b-12d3-a456-426614174001"),
        span_id=UUID("123e4567-e89b-12d3-a456-426614174001"),
        body=NodeExecutionInitiatedBody(
            node_definition=RouterNode,
            inputs={},
        ),
    )

    serialized = router_node_event.model_dump(mode="json")
    assert "exclude_from_monitoring" in serialized["body"]["node_definition"]
    assert serialized["body"]["node_definition"]["exclude_from_monitoring"] is True

    # Test with ElseNode
    else_node_event = NodeExecutionInitiatedEvent(
        id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        trace_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        body=NodeExecutionInitiatedBody(
            node_definition=ElseNode,
            inputs={},
        ),
    )

    serialized = else_node_event.model_dump(mode="json")
    assert "exclude_from_monitoring" in serialized["body"]["node_definition"]
    assert serialized["body"]["node_definition"]["exclude_from_monitoring"] is True


def test_event_max_size__outputs_redacted_when_exceeds_limit():
    """
    Tests that event outputs are redacted when serialized size exceeds event_max_size.
    """

    # GIVEN a workflow with a node
    workflow = MockWorkflow()

    # WHEN the workflow is streamed with a very small event_max_size
    events = list(
        workflow.stream(inputs=MockInputs(foo="bar"), event_filter=all_workflow_event_filter, event_max_size=10)
    )

    # THEN both node and workflow fulfilled events should have redacted outputs
    node_fulfilled_events = [e for e in events if e.name == "node.execution.fulfilled"]
    workflow_fulfilled_events = [e for e in events if e.name == "workflow.execution.fulfilled"]

    assert len(node_fulfilled_events) > 0, "Expected at least one node fulfilled event"
    assert len(workflow_fulfilled_events) == 1, "Expected exactly one workflow fulfilled event"

    # AND the node fulfilled event outputs should be empty
    node_serialized = node_fulfilled_events[0].model_dump(mode="json")
    assert node_serialized["body"]["outputs"] == {}

    # AND the serialized node event should be parseable by the client library
    ClientNodeExecutionFulfilledEvent.model_validate(node_serialized)

    # AND the workflow fulfilled event outputs should be empty
    workflow_serialized = workflow_fulfilled_events[0].model_dump(mode="json")
    assert workflow_serialized["body"]["outputs"] == {}

    # AND the serialized workflow event should be parseable by the client library
    ClientWorkflowExecutionFulfilledEvent.model_validate(workflow_serialized)


def test_event_max_size__outputs_preserved_when_under_limit():
    """
    Tests that event outputs are preserved when serialized size is under event_max_size.
    """

    # GIVEN a workflow with a node that produces outputs
    class OutputNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str = "hello world"

    class OutputWorkflow(BaseWorkflow[MockInputs, BaseState]):
        graph = OutputNode

        class Outputs(BaseWorkflow.Outputs):
            final = OutputNode.Outputs.result

    workflow = OutputWorkflow()

    # WHEN the workflow is streamed with a large event_max_size
    events = list(
        workflow.stream(inputs=MockInputs(foo="bar"), event_filter=all_workflow_event_filter, event_max_size=100000)
    )

    # THEN both node and workflow fulfilled events should have their outputs preserved
    node_fulfilled_events = [e for e in events if e.name == "node.execution.fulfilled"]
    workflow_fulfilled_events = [e for e in events if e.name == "workflow.execution.fulfilled"]

    assert len(node_fulfilled_events) > 0, "Expected at least one node fulfilled event"
    assert len(workflow_fulfilled_events) == 1, "Expected exactly one workflow fulfilled event"

    # AND the node fulfilled event outputs should contain the result
    node_serialized = node_fulfilled_events[0].model_dump(mode="json")
    assert node_serialized["body"]["outputs"]["result"] == "hello world"

    # AND the serialized node event should be parseable by the client library
    ClientNodeExecutionFulfilledEvent.model_validate(node_serialized)

    # AND the workflow fulfilled event outputs should contain the final output
    workflow_serialized = workflow_fulfilled_events[0].model_dump(mode="json")
    assert workflow_serialized["body"]["outputs"]["final"] == "hello world"

    # AND the serialized workflow event should be parseable by the client library
    ClientWorkflowExecutionFulfilledEvent.model_validate(workflow_serialized)


def test_node_execution_initiated_event__generator_input_serializes_gracefully():
    """
    Tests that NodeExecutionInitiatedEvent with a generator input serializes without error.

    This prevents PydanticSerializationError when workflow events contain generator
    objects that cannot be JSON serialized. The generator should be converted to
    a string representation.
    """

    # GIVEN a generator object
    def my_generator():
        yield 1
        yield 2

    gen = my_generator()

    # AND a NodeExecutionInitiatedEvent with the generator as an input value
    event = NodeExecutionInitiatedEvent(
        id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        trace_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        body=NodeExecutionInitiatedBody(
            node_definition=MockNode,
            inputs={
                MockNode.node_foo: gen,
            },
        ),
    )

    # WHEN we serialize the event using model_dump (the same path used by workflow server)
    serialized = event.model_dump(mode="json")

    # THEN the serialization succeeds and the generator is converted to a string
    assert serialized["body"]["inputs"]["node_foo"] == "<generator object>"

    # AND the span_id is preserved correctly
    assert serialized["span_id"] == "123e4567-e89b-12d3-a456-426614174000"
    assert serialized["trace_id"] == "123e4567-e89b-12d3-a456-426614174000"
