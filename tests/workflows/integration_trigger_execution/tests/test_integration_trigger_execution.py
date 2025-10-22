"""Comprehensive integration tests for IntegrationTrigger runtime execution."""

import pytest

from vellum.workflows.exceptions import WorkflowInitializationException

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
        event_data={
            "message": "Test message",
            "channel": "C123456",
            "user": "U789012",
        }
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
        event_data={
            "message": "Streaming test",
            "channel": "C999999",
            "user": "U111111",
        }
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
    """Test that workflow raises error when IntegrationTrigger present but trigger missing."""
    # GIVEN a workflow with SlackMessageTrigger
    workflow = SimpleSlackWorkflow()

    # WHEN we run the workflow without trigger
    # THEN it should raise WorkflowInitializationException
    with pytest.raises(WorkflowInitializationException) as exc_info:
        workflow.run()

    assert "IntegrationTrigger" in str(exc_info.value)
    assert "trigger" in str(exc_info.value)


def test_error_when_trigger_event_provided_but_no_integration_trigger():
    """Test that workflow raises error when trigger provided but no IntegrationTrigger in workflow."""
    # GIVEN a workflow without IntegrationTrigger
    workflow = NoTriggerWorkflow()

    # AND a trigger instance
    trigger = SlackMessageTrigger(
        event_data={
            "message": "This should fail",
            "channel": "C123456",
            "user": "U789012",
        }
    )

    # WHEN we run the workflow with trigger
    # THEN it should raise WorkflowInitializationException
    with pytest.raises(WorkflowInitializationException) as exc_info:
        workflow.run(trigger=trigger)

    assert "trigger provided" in str(exc_info.value)
    assert "does not have an IntegrationTrigger" in str(exc_info.value)


def test_no_trigger_workflow_runs_without_trigger_event():
    """Test that workflow without IntegrationTrigger can run without trigger."""
    # GIVEN a workflow without IntegrationTrigger
    workflow = NoTriggerWorkflow()

    # WHEN we run the workflow without trigger
    result = workflow.run()

    # THEN it should execute successfully
    assert result.name == "workflow.execution.fulfilled"
    assert result.outputs.result == "No trigger workflow"


def test_trigger_attributes_accessible_in_nodes():
    """Test that all trigger attribute fields are accessible in downstream nodes."""
    # GIVEN a workflow with SlackMessageTrigger
    workflow = SimpleSlackWorkflow()

    # AND a comprehensive Slack trigger instance
    trigger = SlackMessageTrigger(
        event_data={
            "message": "Complete test",
            "channel": "C111111",
            "user": "U222222",
        }
    )

    # WHEN we run the workflow
    result = workflow.run(trigger=trigger)

    # THEN it should successfully access trigger attributes
    assert result.name == "workflow.execution.fulfilled"
    assert result.outputs.result == "Received 'Complete test' from channel C111111"


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
        event_data={
            "message": "Multi-trigger test",
            "channel": "C333333",
            "user": "U444444",
        }
    )

    # WHEN we run the workflow with trigger (Slack trigger path)
    result = workflow.run(trigger=trigger)

    # THEN it should execute successfully via SlackTrigger path
    assert result.name == "workflow.execution.fulfilled"
    assert result.outputs.slack_result == "Slack: Multi-trigger test"


def test_trigger_event_with_minimal_payload():
    """Test that trigger works with minimal valid payload."""
    # GIVEN a workflow with SlackMessageTrigger
    workflow = SimpleSlackWorkflow()

    # AND a minimal trigger instance (VellumIntegrationTrigger handles missing fields)
    trigger = SlackMessageTrigger(
        event_data={
            "message": "Minimal",
            "channel": "C000000",
            "user": "U000000",
        }
    )

    # WHEN we run the workflow
    result = workflow.run(trigger=trigger)

    # THEN it should execute successfully
    assert result.name == "workflow.execution.fulfilled"
    assert result.outputs.result == "Received 'Minimal' from channel C000000"


def test_stream_with_multiple_triggers_slack_path():
    """Test workflow.stream() with multiple triggers using Slack path."""
    # GIVEN a workflow with both triggers
    workflow = MultiTriggerWorkflow()

    # AND a Slack trigger instance
    trigger = SlackMessageTrigger(
        event_data={
            "message": "Stream multi-trigger",
            "channel": "C555555",
            "user": "U666666",
        }
    )

    # WHEN we stream with trigger
    events = list(workflow.stream(trigger=trigger))

    # THEN it should complete successfully
    assert len(events) > 0
    last_event = events[-1]
    assert last_event.name == "workflow.execution.fulfilled"
    assert last_event.outputs.slack_result == "Slack: Stream multi-trigger"
