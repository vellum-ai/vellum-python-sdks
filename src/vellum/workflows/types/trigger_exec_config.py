"""
Execution configuration dataclasses for integration triggers.

These classes define the structure of execution configuration data that is
sent to/from the backend for integration triggers. They are used during
serialization and deserialization of trigger configurations.
"""

from typing import Any, Dict, Literal, Optional

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
    integration provider. It includes the provider type, integration name, trigger name,
    and optional dynamic attributes.

    Examples:
        >>> config = ComposioIntegrationTriggerExecConfig(
        ...     provider="COMPOSIO",
        ...     integration_name="SLACK",
        ...     trigger_name="SLACK_NEW_MESSAGE",
        ...     attributes={"channel": "C123456"}
        ... )
        >>> config.provider
        <VellumIntegrationProviderType.COMPOSIO: 'COMPOSIO'>

    Attributes:
        type: Always "COMPOSIO_INTEGRATION_TRIGGER" for this config type
        provider: The integration provider (e.g., COMPOSIO)
        integration_name: The integration identifier (e.g., "SLACK", "GITHUB")
        trigger_name: The specific trigger identifier (e.g., "SLACK_NEW_MESSAGE")
        attributes: Optional dictionary of trigger-specific configuration attributes
    """

    type: Literal["COMPOSIO_INTEGRATION_TRIGGER"] = "COMPOSIO_INTEGRATION_TRIGGER"
    provider: VellumIntegrationProviderType = Field(..., description="The integration provider (e.g., COMPOSIO)")
    integration_name: str = Field(..., description="The integration name (e.g., 'SLACK', 'GITHUB')")
    trigger_name: str = Field(..., description="The specific trigger name (e.g., 'SLACK_NEW_MESSAGE')")
    attributes: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional trigger-specific configuration attributes"
    )
