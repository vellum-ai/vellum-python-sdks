"""Example SlackMessageTrigger for testing."""

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.triggers.vellum_integration import VellumIntegrationTrigger


class SlackMessageTrigger(VellumIntegrationTrigger):
    """Example Slack message trigger for testing runtime execution."""

    # Event attributes - populated from event_data at instantiation
    message: str
    channel: str
    user: str

    class Config(VellumIntegrationTrigger.Config):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
