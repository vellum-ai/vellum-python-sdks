import pytest
from uuid import uuid4
from typing import Optional

from vellum.workflows.events.workflow import WorkflowExecutionInitiatedBody, WorkflowExecutionInitiatedEvent
from vellum.workflows.inputs.base import BaseInputs
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
def test_event_enricher_static_workflow(is_dynamic: bool, expected_config: Optional[dict]):
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
    event_enricher(event)

    # AND workflow_version_exec_config is set to the expected config
    assert event.body.workflow_version_exec_config == expected_config
