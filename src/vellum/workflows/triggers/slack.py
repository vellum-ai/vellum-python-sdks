from typing import Optional

from vellum.workflows.triggers.integration import IntegrationTrigger


class SlackTrigger(IntegrationTrigger):
    """
    Trigger for Slack events (messages, mentions, reactions, etc.).

    SlackTrigger enables workflows to be initiated from Slack events such as
    messages in channels, direct messages, app mentions, or reactions. The trigger
    parses Slack webhook payloads and provides structured attributes that downstream
    nodes can reference.

    Examples:
        Basic Slack message trigger:
            >>> class MyWorkflow(BaseWorkflow):
            ...     graph = SlackTrigger >> ProcessMessageNode

        Access trigger attributes in nodes:
            >>> class ProcessMessageNode(BaseNode):
            ...     class Outputs(BaseNode.Outputs):
            ...         response = SlackTrigger.message

        Multiple entry points:
            >>> class MyWorkflow(BaseWorkflow):
            ...     graph = {
            ...         SlackTrigger >> ProcessSlackNode,
            ...         ManualTrigger >> ProcessManualNode,
            ...     }

    Attributes:
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

    message: str
    channel: str
    user: str
    timestamp: str
    thread_ts: Optional[str]
    event_type: str

    def __init__(self, event_data: dict):
        """
        Initialize SlackTrigger with Slack webhook payload.

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
            >>> trigger = SlackTrigger(slack_payload)
            >>> trigger.message
            'Hello!'
        """
        # Call parent init
        super().__init__(event_data)

        # Extract from Slack's event structure
        event = event_data.get("event", {})

        # Populate trigger attributes
        self.message = event.get("text", "")
        self.channel = event.get("channel", "")
        self.user = event.get("user", "")
        self.timestamp = event.get("ts", "")
        self.thread_ts = event.get("thread_ts")
        self.event_type = event.get("type", "message")
