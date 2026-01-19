"""Tests for validation when a workflow has no triggers and no entrypoint node."""

import pytest

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.state.base import BaseState
from vellum_ee.workflows.display.utils.exceptions import WorkflowValidationError
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_workflow_serialization_error__no_triggers_no_entrypoint():
    """
    Tests that serialization raises an error when a workflow has no triggers and no entrypoint node.
    """

    # GIVEN a workflow with an empty graph (no triggers and no entrypoint nodes)
    class EmptyWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = set()

    # WHEN we attempt to serialize the workflow
    workflow_display = get_workflow_display(workflow_class=EmptyWorkflow)

    # THEN it should raise a WorkflowValidationError about missing triggers and entrypoints
    with pytest.raises(WorkflowValidationError) as exc_info:
        workflow_display.serialize()

    # AND the error message should be exact and descriptive
    error_message = str(exc_info.value)
    assert error_message == (
        "Workflow validation error in EmptyWorkflow: "
        "Workflow has no triggers and no entrypoint nodes. "
        "A workflow must have at least one trigger or one node in its graph."
    )
