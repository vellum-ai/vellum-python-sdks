from abc import ABC
from typing import Any, ClassVar, Dict

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.triggers.base import BaseTrigger, BaseTriggerMeta


class IntegrationTriggerMeta(BaseTriggerMeta):
    """
    Custom metaclass for IntegrationTrigger.

    This metaclass extends BaseTriggerMeta to automatically convert type annotations
    into TriggerAttributeReference objects during class creation. This enables trigger
    attributes to be referenced in workflow graphs while maintaining type safety.
    """

    def __new__(mcs, name: str, bases: tuple, namespace: dict, **kwargs: Any) -> "IntegrationTriggerMeta":
        """Create a new trigger class and set up attribute references."""
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        # Process __annotations__ to create TriggerAttributeReference for each attribute
        # Only process if class has Config and annotations
        has_config = hasattr(cls, "Config") and "Config" in namespace
        if has_config and hasattr(cls, "__annotations__"):
            # Create TriggerAttributeReference for each annotated attribute
            for attr_name, attr_type in cls.__annotations__.items():
                # Skip special attributes and Config
                if attr_name.startswith("_") or attr_name == "Config":
                    continue

                # Create reference with proper type
                reference = TriggerAttributeReference(
                    name=attr_name, types=(attr_type,), instance=None, trigger_class=cls
                )
                # Set as class attribute so it's directly accessible
                setattr(cls, attr_name, reference)

        return cls


class IntegrationTrigger(BaseTrigger, ABC, metaclass=IntegrationTriggerMeta):
    """
    Base class for Vellum-managed integration triggers.

    Subclasses define two types of attributes:
    1. **Config class**: Specifies how the trigger is configured (provider, integration_name, slug)
       - These are configuration details users shouldn't need to interact with directly
    2. **Top-level type annotations**: Define the webhook event payload structure (message, user, channel, etc.)
       - These become TriggerAttributeReference that can be referenced in workflow nodes

    Examples:
        Create a Slack trigger:
            >>> class SlackNewMessageTrigger(IntegrationTrigger):
            ...     # Event attributes (webhook payload structure)
            ...     message: str
            ...     user: str
            ...     channel: str
            ...     timestamp: float
            ...
            ...     # Configuration (how trigger is set up)
            ...     class Config(IntegrationTrigger.Config):
            ...         provider = VellumIntegrationProviderType.COMPOSIO
            ...         integration_name = "SLACK"
            ...         slug = "slack_new_message"

        Use in workflow graph:
            >>> class MyWorkflow(BaseWorkflow):
            ...     graph = SlackNewMessageTrigger >> ProcessMessageNode

        Reference trigger attributes in nodes:
            >>> class ProcessNode(BaseNode):
            ...     class Outputs(BaseNode.Outputs):
            ...         text = SlackNewMessageTrigger.message
            ...         channel = SlackNewMessageTrigger.channel

        Instantiate for testing:
            >>> trigger = SlackNewMessageTrigger(
            ...     message="Hello world",
            ...     channel="C123456",
            ...     user="U123",
            ...     timestamp=1234567890.0,
            ... )
            >>> trigger.message
            'Hello world'
    """

    class Config:
        """
        Configuration for IntegrationTrigger subclasses.

        Defines how the trigger connects to the integration provider. These settings
        specify which integration and which specific trigger type to use.
        """

        provider: ClassVar[VellumIntegrationProviderType]
        integration_name: ClassVar[str]
        slug: ClassVar[str]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Validate that subclasses define required Config class with all required fields."""
        super().__init_subclass__(**kwargs)

        # Skip validation for the base class itself
        if cls.__name__ == "IntegrationTrigger":
            return

        # Require Config class with required fields
        if not hasattr(cls, "Config") or cls.Config is IntegrationTrigger.Config:
            raise TypeError(
                f"{cls.__name__} must define a nested Config class. "
                f"Example:\n"
                f"  class {cls.__name__}(IntegrationTrigger):\n"
                f"      message: str\n"
                f"      class Config(IntegrationTrigger.Config):\n"
                f"          provider = VellumIntegrationProviderType.COMPOSIO\n"
                f"          integration_name = 'SLACK'\n"
                f"          slug = 'slack_new_message'"
            )

        # Validate Config class has required fields
        config_cls = cls.Config
        required_fields = ["provider", "integration_name", "slug"]
        for field in required_fields:
            if not hasattr(config_cls, field):
                raise TypeError(
                    f"{cls.__name__}.Config must define '{field}'. " f"Required fields: {', '.join(required_fields)}"
                )

    def __init__(self, **kwargs: Any):
        """
        Initialize trigger with event data from the integration.

        The trigger dynamically populates its attributes based on the kwargs
        dictionary keys. Any key in kwargs becomes an accessible attribute.

        Examples:
            >>> class SlackTrigger(IntegrationTrigger):
            ...     message: str
            ...     channel: str
            ...     user: str
            ...
            ...     class Config(IntegrationTrigger.Config):
            ...         provider = VellumIntegrationProviderType.COMPOSIO
            ...         integration_name = "SLACK"
            ...         slug = "slack_new_message"
            >>> trigger = SlackTrigger(
            ...     message="Hello",
            ...     channel="C123",
            ...     user="U456"
            ... )
            >>> trigger.message
            'Hello'
            >>> trigger.channel
            'C123'
        """
        super().__init__(**kwargs)

        # Dynamically populate instance attributes from kwargs.
        # This allows any key in kwargs to become an accessible attribute:
        # kwargs={"message": "Hi"} → trigger.message == "Hi"
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_trigger_attribute_values(self) -> Dict["TriggerAttributeReference[Any]", Any]:
        """
        Materialize attribute descriptor/value pairs for this trigger instance.

        For IntegrationTrigger, this includes all dynamic attributes from event_data.
        """
        attribute_values: Dict["TriggerAttributeReference[Any]", Any] = {}

        # Unlike the base class which iterates over type(self) (predefined annotations),
        # we iterate over event_data keys since our attributes are discovered dynamically
        # from the actual event data received during workflow execution.
        # The base class approach: for reference in type(self)
        # Our approach: for attr_name in self._event_data.keys()
        for attr_name in self._event_data.keys():
            # Get the class-level reference for this attribute (created by __new__ from annotations)
            # Unknown keys can appear in webhook payloads, so gracefully skip them if the
            # trigger class doesn't expose a corresponding reference.
            reference = getattr(type(self), attr_name, None)
            if isinstance(reference, TriggerAttributeReference):
                attribute_values[reference] = getattr(self, attr_name)

        return attribute_values
