"""Tests for SlackTrigger workflow."""

from tests.workflows.slack_trigger_workflow.workflow import SlackTriggerWorkflow


def test_slack_trigger_workflow__basic_execution():
    """Test that SlackTrigger workflow can be instantiated and executed with trigger event."""
    # GIVEN a workflow with SlackTrigger
    workflow = SlackTriggerWorkflow()

    # AND a Slack event payload
    slack_event = {
        "event": {
            "type": "message",
            "text": "Hello from Slack!",
            "channel": "C123456",
            "user": "U123456",
            "ts": "1234567890.123456",
        }
    }

    # WHEN we run the workflow with the trigger event
    result = workflow.run(trigger_event=slack_event)

    # THEN it should execute successfully
    assert result.name == "workflow.execution.fulfilled"
    # AND the node should have processed the message from the trigger
    assert result.outputs.result == "Processed: Hello from Slack!"


def test_slack_trigger_workflow__has_trigger():
    """Test that workflow has SlackTrigger in its graph."""
    # GIVEN the SlackTrigger workflow
    # WHEN we check its subgraphs
    subgraphs = SlackTriggerWorkflow.get_subgraphs()

    # THEN it should have trigger edges
    has_trigger = False
    for subgraph in subgraphs:
        if list(subgraph.trigger_edges):
            has_trigger = True
            break

    assert has_trigger, "Workflow should have trigger edges"


def test_slack_trigger_workflow__serialization():
    """Test that workflow with SlackTrigger can be serialized."""
    from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

    # GIVEN the SlackTrigger workflow
    # WHEN we serialize it
    result = get_workflow_display(workflow_class=SlackTriggerWorkflow).serialize()

    # THEN it should have triggers
    assert "triggers" in result
    assert len(result["triggers"]) == 1

    # AND the trigger should be SLACK_MESSAGE type
    trigger = result["triggers"][0]
    assert trigger["type"] == "SLACK_MESSAGE"

    # AND the trigger should have outputs
    assert "outputs" in trigger
    assert len(trigger["outputs"]) == 6  # All SlackTrigger output fields
