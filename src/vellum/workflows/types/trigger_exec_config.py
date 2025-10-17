"""
Execution configuration dataclasses for integration triggers.

These classes define the structure of execution configuration data that is
sent to/from the backend for integration triggers. They are used during
serialization and deserialization of trigger configurations.
"""

from typing import Any, Dict, Literal

from pydantic import Field

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.constants import VellumIntegrationProviderType


class BaseIntegrationTriggerExecConfig(UniversalBaseModel):
    """
    Base class for integration trigger execution configurations.

    This class defines the common structure for all integration trigger exec configs,
    regardless of the provider. Specific providers should extend this class.
    """

    type: str = Field(..., description="The type of integration trigger exec config")


class ComposioIntegrationTriggerExecConfig(BaseIntegrationTriggerExecConfig):
    """
    Execution configuration for Composio-based integration triggers.

    This configuration is used to identify and execute triggers through the Composio
    integration provider. It includes the provider type, integration name, slug,
    trigger nano ID, and event schema.

    Examples:
        >>> config = ComposioIntegrationTriggerExecConfig(
        ...     provider="COMPOSIO",
        ...     integration_name="SLACK",
        ...     slug="slack_new_message",
        ...     event_attributes={"message": str, "user": str}
        ... )
        >>> config.provider
        <VellumIntegrationProviderType.COMPOSIO: 'COMPOSIO'>

    Attributes:
        type: Always "INTEGRATION" for this config type
        provider: The integration provider (e.g., COMPOSIO)
        integration_name: The integration identifier (e.g., "SLACK", "GITHUB")
        slug: The slug of the integration trigger in Composio
        event_attributes: Dictionary mapping attribute names to their types (schema for event data)
    """

    type: Literal["INTEGRATION"] = "INTEGRATION"
    provider: VellumIntegrationProviderType = Field(..., description="The integration provider (e.g., COMPOSIO)")
    integration_name: str = Field(..., description="The integration name (e.g., 'SLACK', 'GITHUB')")
    slug: str = Field(..., description="The slug of the integration trigger in Composio")
    event_attributes: Dict[str, Any] = Field(
        default_factory=dict, description="Schema of event attributes with their types"
    )
