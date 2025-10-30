"""Example SlackMessageTrigger for testing."""

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.triggers.integration import IntegrationTrigger


class SlackMessageTrigger(IntegrationTrigger):
    """Example Slack message trigger for testing runtime execution."""

    # Event attributes - populated from kwargs at instantiation
    message: str
    channel: str
    user: str

    class Config(IntegrationTrigger.Config):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
