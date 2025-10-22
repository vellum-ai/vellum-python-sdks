"""Tests for P1 #1 - Respect caller-specified entrypoints."""

from tests.workflows.integration_trigger_execution.nodes.slack_message_trigger import SlackMessageTrigger
from tests.workflows.integration_trigger_execution.workflows.multi_trigger_workflow import (
    ManualNode,
    MultiTriggerWorkflow,
    SlackNode,
)


def test_respects_explicit_entrypoint_nodes_with_trigger():
    """Test that entrypoint_nodes are respected when trigger is provided."""
    # Track execution
    executed = []
    original_manual = ManualNode.run
    original_slack = SlackNode.run

    def track_manual(self):
        executed.append("ManualNode")
        return original_manual(self)

    def track_slack(self):
        executed.append("SlackNode")
        return original_slack(self)

    ManualNode.run = track_manual
    SlackNode.run = track_slack

    try:
        workflow = MultiTriggerWorkflow()
        trigger = SlackMessageTrigger(event_data={"message": "Test", "channel": "C123", "user": "U123"})

        # Run with trigger but explicit entrypoint_nodes=[ManualNode]
        result = workflow.run(trigger=trigger, entrypoint_nodes=[ManualNode])

        assert result.name == "workflow.execution.fulfilled"
        assert "ManualNode" in executed
        assert "SlackNode" not in executed  # Should respect entrypoint, not trigger routing
    finally:
        ManualNode.run = original_manual
        SlackNode.run = original_slack


def test_trigger_routing_without_explicit_entrypoints():
    """Baseline: trigger routing works when no explicit entrypoints provided."""
    workflow = MultiTriggerWorkflow()
    trigger = SlackMessageTrigger(event_data={"message": "Test", "channel": "C123", "user": "U123"})

    result = workflow.run(trigger=trigger)

    assert result.name == "workflow.execution.fulfilled"
    assert result.outputs.slack_result == "Slack: Test"
