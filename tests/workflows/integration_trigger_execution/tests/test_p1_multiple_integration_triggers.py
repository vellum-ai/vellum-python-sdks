"""Tests for P1 #2 - Filter by specific IntegrationTrigger subclass."""

import pytest

from vellum.workflows import BaseWorkflow
from vellum.workflows.exceptions import WorkflowInitializationException
from vellum.workflows.nodes.bases import BaseNode

from tests.workflows.integration_trigger_execution.nodes.gmail_trigger import GmailTrigger
from tests.workflows.integration_trigger_execution.nodes.slack_message_trigger import SlackMessageTrigger


class SlackNode(BaseNode):
    message = SlackMessageTrigger.message
    channel = SlackMessageTrigger.channel

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result=f"Slack: {self.message} from {self.channel}")


class GmailNode(BaseNode):
    subject = GmailTrigger.subject
    from_email = GmailTrigger.from_email

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result=f"Gmail: {self.subject} from {self.from_email}")


class MultiIntegrationTriggerWorkflow(BaseWorkflow):
    graph = {SlackMessageTrigger >> SlackNode, GmailTrigger >> GmailNode}

    class Outputs(BaseWorkflow.Outputs):
        slack_result = SlackNode.Outputs.result
        gmail_result = GmailNode.Outputs.result


def test_slack_trigger_only_executes_slack_path():
    """Test that Slack trigger only executes Slack path, not Gmail path."""
    workflow = MultiIntegrationTriggerWorkflow()
    slack_trigger = SlackMessageTrigger(event_data={"message": "Test", "channel": "C123", "user": "U123"})

    result = workflow.run(trigger=slack_trigger)

    assert result.name == "workflow.execution.fulfilled"
    assert result.outputs.slack_result == "Slack: Test from C123"

    # Verify only SlackNode executed
    node_outputs = [str(k) for k in result.body.final_state.meta.node_outputs.keys()]
    assert any("SlackNode" in k for k in node_outputs)
    assert not any("GmailNode" in k for k in node_outputs)


def test_gmail_trigger_only_executes_gmail_path():
    """Test that Gmail trigger only executes Gmail path, not Slack path."""
    workflow = MultiIntegrationTriggerWorkflow()
    gmail_trigger = GmailTrigger(event_data={"subject": "Test", "from_email": "test@example.com", "body": "Body"})

    result = workflow.run(trigger=gmail_trigger)

    assert result.name == "workflow.execution.fulfilled"
    assert result.outputs.gmail_result == "Gmail: Test from test@example.com"

    # Verify only GmailNode executed
    node_outputs = [str(k) for k in result.body.final_state.meta.node_outputs.keys()]
    assert any("GmailNode" in k for k in node_outputs)
    assert not any("SlackNode" in k for k in node_outputs)


def test_validates_trigger_matches_workflow():
    """Test that wrong trigger type raises validation error."""

    class SlackOnlyWorkflow(BaseWorkflow):
        graph = SlackMessageTrigger >> SlackNode

        class Outputs(BaseWorkflow.Outputs):
            result = SlackNode.Outputs.result

    workflow = SlackOnlyWorkflow()
    gmail_trigger = GmailTrigger(event_data={"subject": "Test", "from_email": "test@example.com", "body": "Body"})

    with pytest.raises(WorkflowInitializationException) as exc_info:
        workflow.run(trigger=gmail_trigger)

    assert "trigger" in str(exc_info.value).lower()
