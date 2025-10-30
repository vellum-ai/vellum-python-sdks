"""Example GmailTrigger for testing multiple IntegrationTrigger scenarios."""

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.triggers.vellum_integration import VellumIntegrationTrigger


class GmailTrigger(VellumIntegrationTrigger):
    """Example Gmail trigger for testing runtime execution with multiple triggers."""

    # Event attributes - populated from kwargs at instantiation
    subject: str
    from_email: str
    body: str

    class Config(VellumIntegrationTrigger.Config):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "GMAIL"
        slug = "gmail_new_email"
