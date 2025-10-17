import json
from typing import Any, ClassVar, Dict, Optional, Type, cast

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.triggers.base import BaseTriggerMeta
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum.workflows.types import ComposioIntegrationTriggerExecConfig


class VellumIntegrationTriggerMeta(BaseTriggerMeta):
    """
    Custom metaclass for VellumIntegrationTrigger that supports dynamic attribute discovery.

    This metaclass extends BaseTriggerMeta to enable class-level access to attributes
    that aren't statically defined. When accessing an undefined attribute on a
    VellumIntegrationTrigger class, this metaclass will create a TriggerAttributeReference
    dynamically, allowing triggers to work with attributes discovered from integration
    APIs or event payloads.

    Event attributes (defined as top-level type annotations) are automatically converted to
    TriggerAttributeReference objects during class creation in __new__.
    """

    def __new__(mcs, name: str, bases: tuple, namespace: dict, **kwargs: Any) -> "VellumIntegrationTriggerMeta":
        """Create a new trigger class and set up attribute references."""
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        # Initialize cache if not already present
        if not hasattr(cls, "__trigger_attribute_cache__"):
            cls.__trigger_attribute_cache__ = {}

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
                cls.__trigger_attribute_cache__[attr_name] = reference
                # Set as class attribute so it's directly accessible
                setattr(cls, attr_name, reference)

        return cls

    def __getattribute__(cls, name: str) -> Any:
        """
        Override attribute access to support dynamic attribute discovery.

        For configured VellumIntegrationTrigger classes, this method allows access
        to any attribute name, creating TriggerAttributeReference objects on demand.
        This enables usage like:

            SlackMessage = VellumIntegrationTrigger.for_trigger(
                integration_name="SLACK",
                slug="slack_new_message",
            )
            text = SlackMessage.message  # Creates reference even though 'message' isn't pre-defined

        Args:
            name: The attribute name being accessed

        Returns:
            The attribute value or a dynamically created TriggerAttributeReference
        """
        # Let BaseTriggerMeta handle internal attributes and known attributes
        try:
            return super().__getattribute__(name)
        except AttributeError:
            # Only enable dynamic attribute creation for properly configured trigger classes
            # Check if this class has been marked as configured (set in __init_subclass__ or for_trigger)
            try:
                is_configured_trigger = super().__getattribute__("_is_configured") and not name.startswith("_")
            except AttributeError:
                is_configured_trigger = False

            if is_configured_trigger:
                trigger_cls = cast(Type["VellumIntegrationTrigger"], cls)

                # Check cache first
                cache = super().__getattribute__("__trigger_attribute_cache__")
                if name in cache:
                    return cache[name]

                # Only allow declared annotations (event attributes)
                try:
                    annotations = super().__getattribute__("__annotations__")
                    if name not in annotations:
                        raise AttributeError(
                            f"{cls.__name__} has no attribute '{name}'. "
                            f"Declared attributes: {list(annotations.keys())}"
                        )
                except AttributeError:
                    # No annotations, raise error
                    raise AttributeError(f"{cls.__name__} has no attribute '{name}'. No attributes declared.")

                # Create a new dynamic reference for this attribute
                types = (object,)
                reference = TriggerAttributeReference(name=name, types=types, instance=None, trigger_class=trigger_cls)
                cache[name] = reference
                return reference

            # Not a configured trigger or starts with _, re-raise the AttributeError
            raise


class VellumIntegrationTrigger(IntegrationTrigger, metaclass=VellumIntegrationTriggerMeta):
    """
    Base class for Vellum-managed integration triggers.

    Subclasses define two types of attributes:
    1. **Config class**: Specifies how the trigger is configured (provider, integration_name, slug)
       - These are configuration details users shouldn't need to interact with directly
    2. **Top-level type annotations**: Define the webhook event payload structure (message, user, channel, etc.)
       - These become TriggerAttributeReference that can be referenced in workflow nodes

    Examples:
        Create a Slack trigger:
            >>> class SlackNewMessageTrigger(VellumIntegrationTrigger):
            ...     # Event attributes (webhook payload structure)
            ...     message: str
            ...     user: str
            ...     channel: str
            ...     timestamp: float
            ...
            ...     # Configuration (how trigger is set up)
            ...     class Config(VellumIntegrationTrigger.Config):
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
            >>> trigger = SlackNewMessageTrigger(event_data={
            ...     "message": "Hello world",
            ...     "channel": "C123456",
            ...     "user": "U123",
            ...     "timestamp": 1234567890.0,
            ... })
            >>> trigger.message
            'Hello world'
    """

    class Config:
        """
        Configuration for VellumIntegrationTrigger subclasses.

        Defines how the trigger connects to the integration provider. These settings
        specify which integration and which specific trigger type to use.
        """

        provider: ClassVar[VellumIntegrationProviderType]
        integration_name: ClassVar[str]
        slug: ClassVar[str]

    # Cache for generated trigger classes to ensure consistency
    _trigger_class_cache: ClassVar[Dict[tuple, Type["VellumIntegrationTrigger"]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Validate that subclasses define required Config class with all required fields."""
        super().__init_subclass__(**kwargs)

        # Skip validation for the base class itself
        if cls.__name__ == "VellumIntegrationTrigger":
            return

        # Skip validation for dynamically created classes (they use dynamic attributes)
        if cls.__name__.startswith("VellumIntegrationTrigger_"):
            return

        # Require Config class with required fields
        if not hasattr(cls, "Config") or cls.Config is VellumIntegrationTrigger.Config:
            raise TypeError(
                f"{cls.__name__} must define a nested Config class. "
                f"Example:\n"
                f"  class {cls.__name__}(VellumIntegrationTrigger):\n"
                f"      message: str\n"
                f"      class Config(VellumIntegrationTrigger.Config):\n"
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

        # Copy Config attributes to class level for easy access
        cls.provider = config_cls.provider
        cls.integration_name = config_cls.integration_name
        cls.slug = config_cls.slug

        # Mark as configured for simplified detection in __getattribute__
        cls._is_configured = True

    @classmethod
    def _freeze_attributes(cls, attributes: Dict[str, Any]) -> str:
        """
        Convert attributes dict to hashable string for caching.

        Attributes must be JSON-serializable since they're sent to the backend
        via ComposioIntegrationTriggerExecConfig. This method fails fast if
        attributes contain non-JSON-serializable types.

        Args:
            attributes: Dictionary of trigger attributes

        Returns:
            JSON string representation with sorted keys for deterministic hashing

        Raises:
            ValueError: If attributes are not JSON-serializable
        """
        if not attributes:
            return ""

        try:
            # Use json.dumps with sort_keys for deterministic output
            return json.dumps(attributes, sort_keys=True)
        except (TypeError, ValueError) as e:
            raise ValueError(
                f"Trigger attributes must be JSON-serializable (str, int, float, bool, None, list, dict). "
                f"Got non-serializable value: {e}"
            ) from e

    def __init__(self, event_data: dict):
        """
        Initialize trigger with event data from the integration.

        The trigger dynamically populates its attributes based on the event_data
        dictionary keys. Any key in event_data becomes an accessible attribute.

        Args:
            event_data: Raw event data from the integration. Keys become trigger attributes.

        Examples:
            >>> SlackMessage = VellumIntegrationTrigger.for_trigger(
            ...     integration_name="SLACK",
            ...     slug="slack_new_message",
            ...     trigger_nano_id="abc123"
            ... )
            >>> trigger = SlackMessage(event_data={
            ...     "message": "Hello",
            ...     "channel": "C123",
            ...     "user": "U456"
            ... })
            >>> trigger.message
            'Hello'
            >>> trigger.channel
            'C123'
        """
        super().__init__(event_data)

        # Dynamically populate instance attributes from event_data.
        # This allows any key in event_data to become an accessible attribute:
        # event_data={"message": "Hi"} → trigger.message == "Hi"
        for key, value in event_data.items():
            setattr(self, key, value)

    def to_trigger_attribute_values(self) -> Dict["TriggerAttributeReference[Any]", Any]:
        """
        Materialize attribute descriptor/value pairs for this trigger instance.

        For VellumIntegrationTrigger, this includes all dynamic attributes from event_data.
        """
        attribute_values: Dict["TriggerAttributeReference[Any]", Any] = {}

        # Unlike the base class which iterates over type(self) (predefined annotations),
        # we iterate over event_data keys since our attributes are discovered dynamically
        # from the actual event data received during workflow execution.
        # The base class approach: for reference in type(self)
        # Our approach: for attr_name in self._event_data.keys()
        for attr_name in self._event_data.keys():
            # Get the class-level reference for this attribute
            # This will create it via our custom metaclass if it doesn't exist
            reference = getattr(type(self), attr_name)
            if isinstance(reference, TriggerAttributeReference):
                attribute_values[reference] = getattr(self, attr_name)

        return attribute_values

    @classmethod
    def to_exec_config(cls) -> ComposioIntegrationTriggerExecConfig:
        """
        Generate execution configuration for serialization.

        This method creates a ComposioIntegrationTriggerExecConfig from the trigger
        class's configuration (from Config class) and event attributes (from top-level
        type annotations), which is used during serialization to the backend.

        Returns:
            ComposioIntegrationTriggerExecConfig with configuration and event attribute schema

        Raises:
            AttributeError: If called on base VellumIntegrationTrigger

        Examples:
            >>> class SlackTrigger(VellumIntegrationTrigger):
            ...     # Event attributes
            ...     message: str
            ...     user: str
            ...
            ...     # Configuration
            ...     class Config(VellumIntegrationTrigger.Config):
            ...         provider = VellumIntegrationProviderType.COMPOSIO
            ...         integration_name = "SLACK"
            ...         slug = "slack_new_message"
            >>> exec_config = SlackTrigger.to_exec_config()
            >>> exec_config.slug
            'slack_new_message'
            >>> exec_config.event_attributes
            {'message': <class 'str'>, 'user': <class 'str'>}
        """
        if not hasattr(cls, "slug"):
            raise AttributeError(
                "to_exec_config() can only be called on configured VellumIntegrationTrigger subclasses, "
                "not on the base class."
            )

        # Build event_attributes from annotations
        event_attributes: Dict[str, Any] = {}
        if hasattr(cls, "__annotations__"):
            event_attributes = {
                name: type_
                for name, type_ in cls.__annotations__.items()
                if not name.startswith("_") and name != "Config"
            }

        return ComposioIntegrationTriggerExecConfig(
            provider=cls.provider,
            integration_name=cls.integration_name,
            slug=cls.slug,
            event_attributes=event_attributes,
        )

    @classmethod
    def for_trigger(
        cls,
        integration_name: str,
        slug: str,
        trigger_nano_id: str,
        provider: str = "COMPOSIO",
        filter_attributes: Optional[Dict[str, Any]] = None,
    ) -> Type["VellumIntegrationTrigger"]:
        """
        Factory method to create a new trigger class for a specific integration trigger.

        This method generates a unique trigger class that can be used in workflow graphs
        and node definitions. Each unique combination of provider, integration_name,
        slug, and trigger_nano_id produces the same class instance (cached).

        Args:
            integration_name: The integration identifier (e.g., "SLACK", "GITHUB")
            slug: The slug of the integration trigger in Composio (e.g., "slack_new_message")
            trigger_nano_id: Composio's unique trigger identifier used for event matching
            provider: The integration provider (default: "COMPOSIO")
            filter_attributes: Optional dict of trigger-specific configuration attributes
                used for filtering events. For example, {"channel": "C123456"} to only
                match events from a specific Slack channel.

        Returns:
            A new trigger class configured for the specified integration trigger

        Examples:
            >>> SlackNewMessage = VellumIntegrationTrigger.for_trigger(
            ...     integration_name="SLACK",
            ...     slug="slack_new_message",
            ...     trigger_nano_id="abc123def456",
            ...     filter_attributes={"channel": "C123456"}
            ... )
            >>> type(SlackNewMessage).__name__
            'VellumIntegrationTrigger_COMPOSIO_SLACK_slack_new_message'
            >>>
            >>> # Use in workflow
            >>> class MyWorkflow(BaseWorkflow):
            ...     graph = SlackNewMessage >> ProcessNode

        Note:
            The generated class has proper __name__, __module__, and __qualname__
            for correct serialization and attribute ID generation.
        """
        # Validate and normalize provider
        provider_enum = VellumIntegrationProviderType(provider)

        # Normalize filter_attributes
        attrs = filter_attributes or {}

        # Create cache key - include all identifying parameters including filter_attributes
        # Convert filter_attributes dict to a hashable representation for caching
        frozen_attrs = cls._freeze_attributes(attrs)
        cache_key = (
            provider_enum.value,
            integration_name,
            slug,
            trigger_nano_id,
            frozen_attrs,
        )

        # Return cached class if it exists
        if cache_key in cls._trigger_class_cache:
            return cls._trigger_class_cache[cache_key]

        # Generate unique class name including provider to avoid collisions across providers
        class_name = f"VellumIntegrationTrigger_{provider_enum.value}_{integration_name}_{slug}"

        # Create the new trigger class
        trigger_class = type(
            class_name,
            (cls,),
            {
                "provider": provider_enum,
                "integration_name": integration_name,
                "slug": slug,
                "trigger_nano_id": trigger_nano_id,
                "filter_attributes": attrs,
                "__module__": cls.__module__,
                # Explicitly set __qualname__ to match __name__ for deterministic UUID generation.
                # UUIDs are generated from __qualname__, so this must be consistent and unique
                # across different trigger configurations to prevent ID collisions.
                "__qualname__": class_name,
                # Initialize cache attributes that would normally be set by BaseTriggerMeta.__new__
                # Since we're using type() directly, we need to set these ourselves
                "__trigger_attribute_cache__": {},
                # Mark as configured for simplified detection in __getattribute__
                "_is_configured": True,
            },
        )

        # Cache the generated class
        cls._trigger_class_cache[cache_key] = trigger_class

        return trigger_class
