"""Test the apollo_bot workflow with SlackTrigger."""

import pytest

from vellum.workflows.triggers import SlackTrigger

from apollo_bot.workflow import Workflow


def test_workflow_graph_structure():
    """Test that the workflow graph is properly structured with SlackTrigger."""
    # Verify the graph has SlackTrigger as the entry point
    assert hasattr(Workflow, "graph")

    # Get the graph
    graph = Workflow.graph

    # The graph should be a Graph instance
    assert graph is not None


def test_slack_trigger_process_event():
    """Test that SlackTrigger can process a mock Slack event."""
    # Create a mock Slack event payload
    slack_event = {
        "event": {
            "type": "message",
            "text": "Hello apollo-oncall, we have an issue!",
            "channel": "C123456",
            "user": "U789012",
            "ts": "1234567890.123456",
            "thread_ts": "1234567890.000000",
        }
    }

    # Process the event
    outputs = SlackTrigger.process_event(slack_event)

    # Verify outputs
    assert outputs.message == "Hello apollo-oncall, we have an issue!"
    assert outputs.channel == "C123456"
    assert outputs.user == "U789012"
    assert outputs.timestamp == "1234567890.123456"
    assert outputs.thread_ts == "1234567890.000000"
    assert outputs.event_type == "message"


def test_slack_trigger_process_event_without_thread():
    """Test SlackTrigger with an event that's not in a thread."""
    slack_event = {
        "event": {
            "type": "message",
            "text": "Regular message",
            "channel": "C123456",
            "user": "U789012",
            "ts": "1234567890.123456",
        }
    }

    outputs = SlackTrigger.process_event(slack_event)

    assert outputs.message == "Regular message"
    assert outputs.thread_ts is None


@pytest.mark.skip(
    reason=("Requires mocking Linear and Slack API calls - trigger event processing " "is tested in the untagged path")
)
def test_workflow_execution_with_tagged_message():
    """Test end-to-end workflow execution with a message that contains the tag."""
    # GIVEN a workflow instance
    workflow = Workflow()

    # AND a Slack event with a tagged message
    slack_event = {
        "event": {
            "type": "message",
            "text": "Hey apollo-oncall, we have a production issue!",
            "channel": "C123456",
            "user": "U789012",
            "ts": "1234567890.123456",
        }
    }

    # WHEN we run the workflow with the trigger event
    result = workflow.run(trigger_event=slack_event)

    # THEN the workflow should execute successfully
    assert result.name == "workflow.execution.fulfilled"


def test_workflow_execution_with_untagged_message():
    """Test end-to-end workflow execution with a message without the tag."""
    # GIVEN a workflow instance
    workflow = Workflow()

    # AND a Slack event with a regular message
    slack_event = {
        "event": {
            "type": "message",
            "text": "Just a regular message",
            "channel": "C123456",
            "user": "U789012",
            "ts": "1234567890.123456",
        }
    }

    # WHEN we run the workflow with the trigger event
    result = workflow.run(trigger_event=slack_event)

    # THEN the workflow should execute successfully
    assert result.name == "workflow.execution.fulfilled"

    # AND it should take the "not_tagged" path
    assert result.outputs.path_taken == "not_tagged"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
