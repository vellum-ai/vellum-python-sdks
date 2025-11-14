"""Comprehensive integration tests for IntegrationTrigger runtime execution."""

import pytest

from vellum.workflows.exceptions import WorkflowInitializationException
from vellum.workflows.triggers.manual import ManualTrigger

from tests.workflows.integration_trigger_execution.nodes.slack_message_trigger import SlackMessageTrigger
from tests.workflows.integration_trigger_execution.workflows.multi_trigger_workflow import MultiTriggerWorkflow
from tests.workflows.integration_trigger_execution.workflows.no_trigger_workflow import NoTriggerWorkflow
from tests.workflows.integration_trigger_execution.workflows.simple_workflow import SimpleSlackWorkflow


def test_successful_execution_with_trigger_event():
    """Test successful workflow execution with IntegrationTrigger and trigger instance."""
    # GIVEN a workflow with SlackMessageTrigger
    workflow = SimpleSlackWorkflow()

    # AND a valid Slack trigger instance
    trigger = SlackMessageTrigger(
        message="Test message",
        channel="C123456",
        user="U789012",
    )

    # WHEN we run the workflow with the trigger
    result = workflow.run(trigger=trigger)

    # THEN it should execute successfully
    assert result.name == "workflow.execution.fulfilled"

    # AND the node should have access to trigger outputs
    assert result.outputs.result == "Received 'Test message' from channel C123456"


def test_stream_execution_with_trigger_event():
    """Test workflow.stream() works with trigger instance."""
    # GIVEN a workflow with SlackMessageTrigger
    workflow = SimpleSlackWorkflow()

    # AND a valid Slack trigger instance
    trigger = SlackMessageTrigger(
        message="Streaming test",
        channel="C999999",
        user="U111111",
    )

    # WHEN we stream the workflow with the trigger
    events = list(workflow.stream(trigger=trigger))

    # THEN we should get workflow events
    assert len(events) > 0

    # AND the final event should be fulfilled
    last_event = events[-1]
    assert last_event.name == "workflow.execution.fulfilled"
    assert last_event.outputs.result == "Received 'Streaming test' from channel C999999"


def test_error_when_trigger_event_missing():
    """Test that workflow with IntegrationTrigger that references attributes fails without trigger data."""
    # GIVEN a workflow with SlackMessageTrigger that references trigger attributes
    workflow = SimpleSlackWorkflow()

    # WHEN we run the workflow without trigger
    result = workflow.run()

    # THEN it should be rejected due to missing trigger attributes
    assert result.name == "workflow.execution.rejected"

    # AND the error should indicate missing trigger attribute
    assert "Missing trigger attribute" in result.body.error.message


def test_error_when_trigger_event_provided_but_no_integration_trigger():
    """Test that workflow raises error when trigger provided but no matching trigger in workflow."""
    # GIVEN a workflow without IntegrationTrigger
    workflow = NoTriggerWorkflow()

    # AND a trigger instance
    trigger = SlackMessageTrigger(
        message="This should fail",
        channel="C123456",
        user="U789012",
    )

    # WHEN we run the workflow with trigger
    # THEN it should raise WorkflowInitializationException
    with pytest.raises(WorkflowInitializationException) as exc_info:
        workflow.run(trigger=trigger)

    assert "not compatible with workflow" in str(exc_info.value)
    assert "SlackMessageTrigger" in str(exc_info.value)
    assert "ManualTrigger" in str(exc_info.value)


def test_no_trigger_workflow_runs_without_trigger_event():
    """Test that workflow without IntegrationTrigger can run without trigger."""
    # GIVEN a workflow without IntegrationTrigger
    workflow = NoTriggerWorkflow()

    # WHEN we run the workflow without trigger
    result = workflow.run()

    # THEN it should execute successfully
    assert result.name == "workflow.execution.fulfilled"
    assert result.outputs.result == "No trigger workflow"


def test_workflow_with_multiple_triggers_manual_path():
    """Test workflow with both ManualTrigger and IntegrationTrigger - manual path."""
    # GIVEN a workflow with both ManualTrigger and IntegrationTrigger
    workflow = MultiTriggerWorkflow()

    # WHEN we run the workflow without trigger_event (manual trigger path)
    result = workflow.run()

    # THEN it should execute successfully via ManualTrigger path
    assert result.name == "workflow.execution.fulfilled"
    # The manual path node should execute
    assert result.outputs.manual_result == "Manual execution"


def test_workflow_with_multiple_triggers_slack_path():
    """Test workflow with both ManualTrigger and IntegrationTrigger - Slack path."""
    # GIVEN a workflow with both ManualTrigger and IntegrationTrigger
    workflow = MultiTriggerWorkflow()

    # AND a Slack trigger instance
    trigger = SlackMessageTrigger(
        message="Multi-trigger test",
        channel="C333333",
        user="U444444",
    )

    # WHEN we run the workflow with trigger (Slack trigger path)
    result = workflow.run(trigger=trigger)

    # THEN it should execute successfully via SlackTrigger path
    assert result.name == "workflow.execution.fulfilled"
    assert result.outputs.slack_result == "Slack: Multi-trigger test"


def test_manual_trigger_instance_can_be_passed():
    """Test that ManualTrigger instance can be passed explicitly (supports BaseTrigger)."""
    # GIVEN a workflow with both ManualTrigger and IntegrationTrigger
    workflow = MultiTriggerWorkflow()

    # AND an explicit ManualTrigger instance
    trigger = ManualTrigger()

    # WHEN we run the workflow with ManualTrigger instance
    result = workflow.run(trigger=trigger)

    # THEN it should execute successfully via ManualTrigger path
    assert result.name == "workflow.execution.fulfilled"
    # The manual path node should execute
    assert result.outputs.manual_result == "Manual execution"


def test_workflow_with_only_manual_trigger_accepts_manual_trigger_instance():
    """Test that workflow with only ManualTrigger accepts ManualTrigger instance."""
    # GIVEN a workflow without IntegrationTrigger (implicit ManualTrigger)
    workflow = NoTriggerWorkflow()

    # AND an explicit ManualTrigger instance
    trigger = ManualTrigger()

    # WHEN we run the workflow with ManualTrigger instance
    result = workflow.run(trigger=trigger)

    # THEN it should execute successfully
    assert result.name == "workflow.execution.fulfilled"
    assert result.outputs.result == "No trigger workflow"


def test_workflow_initiated_event_has_trigger():
    # GIVEN a workflow with an IntegrationTrigger (Slack)
    workflow = SimpleSlackWorkflow()
    trigger = SlackMessageTrigger(message="hello", channel="C1", user="U1")

    # WHEN streaming events
    events = list(workflow.stream(trigger=trigger))

    # THEN the first event is workflow.execution.initiated
    assert len(events) >= 1
    initiated = events[0]
    assert initiated.name == "workflow.execution.initiated"

    # AND the initiated event has the trigger field
    trigger_definition = initiated.body.trigger
    assert trigger_definition is not None
    assert trigger_definition.__name__ == "SlackMessageTrigger"
