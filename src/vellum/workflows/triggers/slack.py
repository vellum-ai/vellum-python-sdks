from typing import Optional

from vellum.workflows.triggers.integration import IntegrationTrigger


class SlackTrigger(IntegrationTrigger):
    """
    Trigger for Slack events (messages, mentions, reactions, etc.).

    SlackTrigger enables workflows to be initiated from Slack events such as
    messages in channels, direct messages, app mentions, or reactions. The trigger
    parses Slack webhook payloads and provides structured outputs that downstream
    nodes can reference.

    Examples:
        Basic Slack message trigger:
            >>> class MyWorkflow(BaseWorkflow):
            ...     graph = SlackTrigger >> ProcessMessageNode

        Access trigger outputs in nodes:
            >>> class ProcessMessageNode(BaseNode):
            ...     class Outputs(BaseNode.Outputs):
            ...         response = SlackTrigger.Outputs.message

        Multiple entry points:
            >>> class MyWorkflow(BaseWorkflow):
            ...     graph = {
            ...         SlackTrigger >> ProcessSlackNode,
            ...         ManualTrigger >> ProcessManualNode,
            ...     }

    Outputs:
        message: str
            The message text from Slack
        channel: str
            Slack channel ID where message was sent
        user: str
            User ID who sent the message
        timestamp: str
            Message timestamp (ts field from Slack)
        thread_ts: Optional[str]
            Thread timestamp if message is in a thread, None otherwise
        event_type: str
            Type of Slack event (e.g., "message", "app_mention")

    Note:
        The trigger expects Slack Event API webhook payloads. For details on
        the payload structure, see: https://api.slack.com/apis/connections/events-api
    """

    class Outputs(IntegrationTrigger.Outputs):
        message: str
        channel: str
        user: str
        timestamp: str
        thread_ts: Optional[str]
        event_type: str

    @classmethod
    def process_event(cls, event_data: dict) -> "SlackTrigger.Outputs":
        """
        Parse Slack webhook payload into trigger outputs.

        Args:
            event_data: Slack event payload from webhook. Expected structure:
                {
                    "event": {
                        "type": "message",
                        "text": "Hello world",
                        "channel": "C123456",
                        "user": "U123456",
                        "ts": "1234567890.123456",
                        "thread_ts": "1234567890.123456"  # optional
                    }
                }

        Returns:
            SlackTrigger.Outputs with parsed data from the Slack event

        Examples:
            >>> slack_payload = {
            ...     "event": {
            ...         "type": "message",
            ...         "text": "Hello!",
            ...         "channel": "C123",
            ...         "user": "U456",
            ...         "ts": "1234567890.123456"
            ...     }
            ... }
            >>> outputs = SlackTrigger.process_event(slack_payload)
            >>> outputs.message
            'Hello!'
        """
        # Extract from Slack's event structure
        event = event_data.get("event", {})

        return cls.Outputs(
            message=event.get("text", ""),
            channel=event.get("channel", ""),
            user=event.get("user", ""),
            timestamp=event.get("ts", ""),
            thread_ts=event.get("thread_ts"),
            event_type=event.get("type", "message"),
        )
