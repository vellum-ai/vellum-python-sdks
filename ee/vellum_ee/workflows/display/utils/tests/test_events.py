import pytest
from uuid import uuid4
from typing import Optional

from vellum.workflows.events.types import NodeParentContext, WorkflowDeploymentParentContext
from vellum.workflows.events.workflow import WorkflowExecutionInitiatedBody, WorkflowExecutionInitiatedEvent
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.utils.events import event_enricher


@pytest.mark.parametrize(
    "is_dynamic,expected_config",
    [
        (False, None),
        (
            True,
            {
                "workflow_raw_data": {
                    "nodes": [
                        {
                            "id": "86607b18-7872-49f3-a592-fda1428f70aa",
                            "type": "ENTRYPOINT",
                            "inputs": [],
                            "data": {
                                "label": "Entrypoint Node",
                                "source_handle_id": "d1fe8f4c-53d7-43a0-b210-73ebdc60bf57",
                            },
                            "display_data": {"position": {"x": 0.0, "y": -50.0}},
                            "base": None,
                            "definition": None,
                        }
                    ],
                    "edges": [],
                    "display_data": {"viewport": {"x": 0.0, "y": 0.0, "zoom": 1.0}},
                    "definition": {
                        "name": "TestWorkflow",
                        "module": ["vellum_ee", "workflows", "display", "utils", "tests", "test_events"],
                    },
                    "output_values": [],
                },
                "input_variables": [],
                "state_variables": [],
                "output_variables": [],
            },
        ),
    ],
)
def test_event_enricher_static_workflow(vellum_client, is_dynamic: bool, expected_config: Optional[dict]):
    """Test event_enricher with a static workflow (is_dynamic=False)."""
    # GIVEN a workflow class with the specified is_dynamic value
    _is_dynamic = is_dynamic

    class TestWorkflow(BaseWorkflow):
        is_dynamic = _is_dynamic

    event: WorkflowExecutionInitiatedEvent = WorkflowExecutionInitiatedEvent(
        trace_id=uuid4(),
        span_id=uuid4(),
        body=WorkflowExecutionInitiatedBody(
            workflow_definition=TestWorkflow,
            inputs=BaseInputs(),
        ),
    )

    # WHEN the event_enricher is called with mocked dependencies
    event_enricher(event, vellum_client)

    # THEN workflow_version_exec_config is set to the expected config
    assert event.body.workflow_version_exec_config == expected_config

    assert event.body.display_context is not None
    assert hasattr(event.body.display_context, "node_displays")
    assert hasattr(event.body.display_context, "workflow_inputs")
    assert hasattr(event.body.display_context, "workflow_outputs")


def test_event_enricher_marks_subworkflow_deployment_as_dynamic(vellum_client):
    """Test that event_enricher treats subworkflow deployments as dynamic."""

    class TestWorkflow(BaseWorkflow):
        is_dynamic = False

        class Outputs(BaseOutputs):
            pass

    event: WorkflowExecutionInitiatedEvent = WorkflowExecutionInitiatedEvent(
        trace_id=uuid4(),
        span_id=uuid4(),
        parent=WorkflowDeploymentParentContext(
            span_id=uuid4(),
            deployment_id=uuid4(),
            deployment_name="test-deployment",
            deployment_history_item_id=uuid4(),
            release_tag_id=uuid4(),
            release_tag_name="test-tag",
            workflow_version_id=uuid4(),
            external_id=None,
            metadata=None,
            parent=NodeParentContext(
                span_id=uuid4(),
                node_definition=TestWorkflow,
                parent=None,
            ),
        ),
        body=WorkflowExecutionInitiatedBody(
            workflow_definition=TestWorkflow,
            inputs=BaseInputs(),
        ),
    )

    enriched_event = event_enricher(event, vellum_client)

    assert enriched_event.name == "workflow.execution.initiated"
    assert hasattr(enriched_event.body, "workflow_version_exec_config")
    assert enriched_event.body.workflow_version_exec_config is not None

    assert enriched_event.body.display_context is not None
    assert hasattr(enriched_event.body.display_context, "node_displays")
    assert hasattr(enriched_event.body.display_context, "workflow_inputs")
    assert hasattr(enriched_event.body.display_context, "workflow_outputs")


def test_event_enricher_with_metadata(vellum_client):
    """Test that event_enricher attaches metadata to server_metadata field."""

    # GIVEN a workflow class
    class TestWorkflow(BaseWorkflow):
        is_dynamic = False

    # AND an event
    event: WorkflowExecutionInitiatedEvent = WorkflowExecutionInitiatedEvent(
        trace_id=uuid4(),
        span_id=uuid4(),
        body=WorkflowExecutionInitiatedBody(
            workflow_definition=TestWorkflow,
            inputs=BaseInputs(),
        ),
    )

    # AND some metadata
    metadata = {"custom_key": "custom_value", "another_key": 123}

    # WHEN the event_enricher is called with metadata
    enriched_event = event_enricher(event, vellum_client, metadata=metadata)

    # THEN the metadata should be attached to server_metadata
    assert enriched_event.name == "workflow.execution.initiated"
    assert enriched_event.body.server_metadata == metadata
