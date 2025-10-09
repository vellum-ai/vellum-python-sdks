"""Comprehensive integration tests for IntegrationTrigger runtime execution."""

import pytest

from vellum.workflows.exceptions import WorkflowInitializationException

from tests.workflows.integration_trigger_execution.workflows.multi_trigger_workflow import MultiTriggerWorkflow
from tests.workflows.integration_trigger_execution.workflows.no_trigger_workflow import NoTriggerWorkflow
from tests.workflows.integration_trigger_execution.workflows.simple_workflow import SimpleSlackWorkflow


def test_successful_execution_with_trigger_event():
    """Test successful workflow execution with IntegrationTrigger and trigger_event."""
    # GIVEN a workflow with SlackTrigger
    workflow = SimpleSlackWorkflow()

    # AND a valid Slack event payload
    slack_event = {
        "event": {
            "type": "message",
            "text": "Test message",
            "channel": "C123456",
            "user": "U789012",
            "ts": "1234567890.123456",
        }
    }

    # WHEN we run the workflow with the trigger event
    result = workflow.run(trigger_event=slack_event)

    # THEN it should execute successfully
    assert result.name == "workflow.execution.fulfilled"

    # AND the node should have access to trigger outputs
    assert result.outputs.result == "Received 'Test message' from channel C123456"


def test_stream_execution_with_trigger_event():
    """Test workflow.stream() works with trigger_event."""
    # GIVEN a workflow with SlackTrigger
    workflow = SimpleSlackWorkflow()

    # AND a valid Slack event payload
    slack_event = {
        "event": {
            "type": "message",
            "text": "Streaming test",
            "channel": "C999999",
            "user": "U111111",
            "ts": "9999999999.999999",
        }
    }

    # WHEN we stream the workflow with the trigger event
    events = list(workflow.stream(trigger_event=slack_event))

    # THEN we should get workflow events
    assert len(events) > 0

    # AND the final event should be fulfilled
    last_event = events[-1]
    assert last_event.name == "workflow.execution.fulfilled"
    assert last_event.outputs.result == "Received 'Streaming test' from channel C999999"


def test_error_when_trigger_event_missing():
    """Test that workflow raises error when IntegrationTrigger present but trigger_event missing."""
    # GIVEN a workflow with SlackTrigger
    workflow = SimpleSlackWorkflow()

    # WHEN we run the workflow without trigger_event
    # THEN it should raise WorkflowInitializationException
    with pytest.raises(WorkflowInitializationException) as exc_info:
        workflow.run()

    assert "IntegrationTrigger" in str(exc_info.value)
    assert "trigger_event" in str(exc_info.value)


def test_error_when_trigger_event_provided_but_no_integration_trigger():
    """Test that workflow raises error when trigger_event provided but no IntegrationTrigger in workflow."""
    # GIVEN a workflow without IntegrationTrigger
    workflow = NoTriggerWorkflow()

    # AND a trigger event
    slack_event = {
        "event": {
            "type": "message",
            "text": "This should fail",
            "channel": "C123456",
            "user": "U789012",
            "ts": "1234567890.123456",
        }
    }

    # WHEN we run the workflow with trigger_event
    # THEN it should raise WorkflowInitializationException
    with pytest.raises(WorkflowInitializationException) as exc_info:
        workflow.run(trigger_event=slack_event)

    assert "trigger_event provided" in str(exc_info.value)
    assert "does not have an IntegrationTrigger" in str(exc_info.value)


def test_no_trigger_workflow_runs_without_trigger_event():
    """Test that workflow without IntegrationTrigger can run without trigger_event."""
    # GIVEN a workflow without IntegrationTrigger
    workflow = NoTriggerWorkflow()

    # WHEN we run the workflow without trigger_event
    result = workflow.run()

    # THEN it should execute successfully
    assert result.name == "workflow.execution.fulfilled"
    assert result.outputs.result == "No trigger workflow"


def test_trigger_outputs_accessible_in_nodes():
    """Test that all trigger output fields are accessible in downstream nodes."""
    # GIVEN a workflow with SlackTrigger
    workflow = SimpleSlackWorkflow()

    # AND a comprehensive Slack event payload
    slack_event = {
        "event": {
            "type": "app_mention",
            "text": "Complete test",
            "channel": "C111111",
            "user": "U222222",
            "ts": "1111111111.111111",
            "thread_ts": "1111111111.000000",
        }
    }

    # WHEN we run the workflow
    result = workflow.run(trigger_event=slack_event)

    # THEN it should successfully access trigger outputs
    assert result.name == "workflow.execution.fulfilled"
    # The SimpleNode only uses message and channel, but all outputs should be available


def test_workflow_with_multiple_triggers_manual_path():
    """Test workflow with both ManualTrigger and IntegrationTrigger - manual path."""
    # GIVEN a workflow with both ManualTrigger and IntegrationTrigger
    workflow = MultiTriggerWorkflow()

    # WHEN we run the workflow without trigger_event (manual trigger path)
    result = workflow.run()

    # THEN it should execute successfully via ManualTrigger path
    assert result.name == "workflow.execution.fulfilled"
    # The manual path node should execute, slack path should not
    assert result.outputs.manual_result == "Manual execution"


def test_workflow_with_multiple_triggers_slack_path():
    """Test workflow with both ManualTrigger and IntegrationTrigger - Slack path."""
    # GIVEN a workflow with both ManualTrigger and IntegrationTrigger
    workflow = MultiTriggerWorkflow()

    # AND a Slack event
    slack_event = {
        "event": {
            "type": "message",
            "text": "Multi-trigger test",
            "channel": "C333333",
            "user": "U444444",
            "ts": "3333333333.333333",
        }
    }

    # WHEN we run the workflow with trigger_event (Slack trigger path)
    result = workflow.run(trigger_event=slack_event)

    # THEN it should execute successfully via SlackTrigger path
    assert result.name == "workflow.execution.fulfilled"
    assert result.outputs.slack_result == "Slack: Multi-trigger test"


def test_trigger_event_with_minimal_slack_payload():
    """Test that trigger_event works with minimal valid Slack payload."""
    # GIVEN a workflow with SlackTrigger
    workflow = SimpleSlackWorkflow()

    # AND a minimal Slack event (only required fields)
    slack_event = {
        "event": {
            # process_event provides defaults for missing fields
        }
    }

    # WHEN we run the workflow
    result = workflow.run(trigger_event=slack_event)

    # THEN it should execute successfully with default values
    assert result.name == "workflow.execution.fulfilled"
    # Empty strings are the defaults from SlackTrigger.process_event
    assert result.outputs.result == "Received '' from channel "
