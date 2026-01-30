"""Tests for validation that trigger-based workflows cannot have workflow inputs."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum.workflows.triggers.manual import ManualTrigger
from vellum.workflows.triggers.schedule import ScheduleTrigger
from vellum_ee.workflows.display.utils.exceptions import WorkflowValidationError
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_trigger_workflow_with_inputs__validation_error():
    """
    Tests that serialization adds an error when a trigger-based workflow has workflow inputs.
    """

    # GIVEN a trigger-based workflow with inputs defined
    class MyInputs(BaseInputs):
        query: str

    class SlackTrigger(IntegrationTrigger):
        message: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "SLACK"
            slug = "slack_new_message"

    class ProcessNode(BaseNode):
        pass

    class TriggerWorkflowWithInputs(BaseWorkflow[MyInputs, BaseState]):
        graph = SlackTrigger >> ProcessNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TriggerWorkflowWithInputs)
    workflow_display.serialize()

    # THEN the display_context should contain a WorkflowValidationError
    errors = list(workflow_display.display_context.errors)
    validation_errors = [e for e in errors if isinstance(e, WorkflowValidationError)]
    assert len(validation_errors) == 1

    # AND the error message should indicate trigger workflows cannot have inputs
    error = validation_errors[0]
    assert "Trigger-based workflows cannot have workflow inputs" in str(error)


def test_scheduled_trigger_workflow_with_inputs__validation_error():
    """
    Tests that serialization adds an error when a ScheduleTrigger workflow has workflow inputs.
    """

    # GIVEN a scheduled trigger workflow with inputs defined
    class MyInputs(BaseInputs):
        query: str

    class DailySchedule(ScheduleTrigger):
        class Config(ScheduleTrigger.Config):
            cron = "0 9 * * *"

    class ProcessNode(BaseNode):
        pass

    class ScheduledWorkflowWithInputs(BaseWorkflow[MyInputs, BaseState]):
        graph = DailySchedule >> ProcessNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=ScheduledWorkflowWithInputs)
    workflow_display.serialize()

    # THEN the display_context should contain a WorkflowValidationError
    errors = list(workflow_display.display_context.errors)
    validation_errors = [e for e in errors if isinstance(e, WorkflowValidationError)]
    assert len(validation_errors) == 1

    # AND the error message should indicate trigger workflows cannot have inputs
    error = validation_errors[0]
    assert "Trigger-based workflows cannot have workflow inputs" in str(error)


def test_manual_trigger_workflow_with_inputs__no_error():
    """
    Tests that ManualTrigger workflows can have workflow inputs without validation errors.
    """

    # GIVEN a ManualTrigger workflow with inputs defined
    class MyInputs(BaseInputs):
        query: str

    class ProcessNode(BaseNode):
        pass

    class ManualWorkflowWithInputs(BaseWorkflow[MyInputs, BaseState]):
        graph = ManualTrigger >> ProcessNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=ManualWorkflowWithInputs)
    workflow_display.serialize()

    # THEN the display_context should NOT contain a WorkflowValidationError about inputs
    errors = list(workflow_display.display_context.errors)
    validation_errors = [
        e for e in errors if isinstance(e, WorkflowValidationError) and "cannot have workflow inputs" in str(e)
    ]
    assert len(validation_errors) == 0


def test_trigger_workflow_without_inputs__no_error():
    """
    Tests that trigger-based workflows without inputs serialize without validation errors.
    """

    # GIVEN a trigger-based workflow without inputs
    class SlackTrigger(IntegrationTrigger):
        message: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "SLACK"
            slug = "slack_new_message"

    class ProcessNode(BaseNode):
        pass

    class TriggerWorkflowWithoutInputs(BaseWorkflow[BaseInputs, BaseState]):
        graph = SlackTrigger >> ProcessNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TriggerWorkflowWithoutInputs)
    workflow_display.serialize()

    # THEN the display_context should NOT contain a WorkflowValidationError about inputs
    errors = list(workflow_display.display_context.errors)
    validation_errors = [
        e for e in errors if isinstance(e, WorkflowValidationError) and "cannot have workflow inputs" in str(e)
    ]
    assert len(validation_errors) == 0
