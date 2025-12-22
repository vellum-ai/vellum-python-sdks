"""Tests for workflow output reference serialization in serialize_value."""

from uuid import UUID

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.base import WorkflowOutputDisplay
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.expressions import serialize_value


def test_serialize_value__workflow_output_reference():
    """Workflow output references are serialized with WORKFLOW_OUTPUT type."""

    # GIVEN a workflow with an output
    class MyWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        class Outputs(BaseWorkflow.Outputs):
            result: str

    workflow_output_ref = MyWorkflow.Outputs.result
    workflow_output_display = WorkflowOutputDisplay(
        id=UUID("12345678-1234-1234-1234-123456789abc"),
        name="result",
    )

    # AND a display context that includes the workflow output
    display_context = WorkflowDisplayContext(
        workflow_output_displays={workflow_output_ref: workflow_output_display},
    )

    # WHEN we serialize the workflow output reference
    result = serialize_value(
        executable_id=UUID("00000000-0000-0000-0000-000000000000"),
        display_context=display_context,
        value=workflow_output_ref,
    )

    # THEN we should get a WORKFLOW_OUTPUT serialization
    assert result == {
        "type": "WORKFLOW_OUTPUT",
        "output_variable_id": "12345678-1234-1234-1234-123456789abc",
    }
