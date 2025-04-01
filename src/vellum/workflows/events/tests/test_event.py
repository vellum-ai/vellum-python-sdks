import pytest
from datetime import datetime
from uuid import UUID

from deepdiff import DeepDiff

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.constants import undefined
from vellum.workflows.errors.types import WorkflowError, WorkflowErrorCode
from vellum.workflows.events.node import (
    NodeExecutionFulfilledBody,
    NodeExecutionFulfilledEvent,
    NodeExecutionInitiatedBody,
    NodeExecutionInitiatedEvent,
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
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.core import VellumSecret
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum.workflows.workflows.base import BaseWorkflow


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
mock_node_uuid = str(uuid4_from_hash(MockNode.__qualname__))


@pytest.mark.parametrize(
    ["event", "expected_json"],
    [
        (
            WorkflowExecutionInitiatedEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
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
                "timestamp": "2024-01-01T12:00:00",
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
                },
                "parent": None,
            },
        ),
        (
            NodeExecutionInitiatedEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
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
                "timestamp": "2024-01-01T12:00:00",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "node.execution.initiated",
                "body": {
                    "node_definition": {
                        "id": mock_node_uuid,
                        "name": "MockNode",
                        "module": module_root + ["events", "tests", "test_event"],
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
            },
        ),
        (
            WorkflowExecutionStreamingEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
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
                "timestamp": "2024-01-01T12:00:00",
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
            },
        ),
        (
            WorkflowExecutionFulfilledEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
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
                "timestamp": "2024-01-01T12:00:00",
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
                },
                "parent": None,
            },
        ),
        (
            WorkflowExecutionRejectedEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
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
                "timestamp": "2024-01-01T12:00:00",
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
                    },
                },
                "parent": None,
            },
        ),
        (
            NodeExecutionStreamingEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
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
                "timestamp": "2024-01-01T12:00:00",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "node.execution.streaming",
                "body": {
                    "node_definition": {
                        "id": mock_node_uuid,
                        "name": "MockNode",
                        "module": module_root + ["events", "tests", "test_event"],
                    },
                    "output": {
                        "name": "example",
                        "value": "foo",
                    },
                },
                "parent": None,
            },
        ),
        (
            NodeExecutionFulfilledEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
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
                "timestamp": "2024-01-01T12:00:00",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "node.execution.fulfilled",
                "body": {
                    "node_definition": {
                        "id": mock_node_uuid,
                        "name": "MockNode",
                        "module": module_root + ["events", "tests", "test_event"],
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
            },
        ),
        (
            NodeExecutionFulfilledEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
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
                "timestamp": "2024-01-01T12:00:00",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "node.execution.fulfilled",
                "body": {
                    "node_definition": {
                        "id": mock_node_uuid,
                        "name": "MockNode",
                        "module": module_root + ["events", "tests", "test_event"],
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
            },
        ),
        (
            NodeExecutionFulfilledEvent(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
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
                "timestamp": "2024-01-01T12:00:00",
                "trace_id": "123e4567-e89b-12d3-a456-426614174000",
                "span_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "node.execution.fulfilled",
                "body": {
                    "node_definition": {
                        "id": mock_node_uuid,
                        "name": "MockNode",
                        "module": module_root + ["events", "tests", "test_event"],
                    },
                    "outputs": {"example": "foo"},
                    "mocked": True,
                },
                "parent": None,
            },
        ),
    ],
    ids=[
        "workflow.execution.initiated",
        "node.execution.initiated",
        "workflow.execution.streaming",
        "workflow.execution.fulfilled",
        "workflow.execution.rejected",
        "node.execution.streaming",
        "node.execution.fulfilled",
        "fulfilled_node_with_undefined_outputs",
        "mocked_node",
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
