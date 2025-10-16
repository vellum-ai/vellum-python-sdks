from uuid import UUID
from typing import Any, ClassVar, Dict, Optional

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.triggers.base import BaseTriggerMeta
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum.workflows.types import ComposioIntegrationTriggerExecConfig
from vellum.workflows.utils.uuids import uuid4_from_hash


class VellumIntegrationTriggerMeta(BaseTriggerMeta):
    """
    Custom metaclass for VellumIntegrationTrigger.

    This metaclass extends BaseTriggerMeta to support the Schema-based attribute definition
    pattern. The __init_subclass__ hook processes Schema inner classes to generate
    TriggerAttributeReference objects for each attribute, enabling type-safe trigger
    attribute access in workflow definitions.
    """

    pass


class VellumIntegrationTrigger(IntegrationTrigger, metaclass=VellumIntegrationTriggerMeta):
    """
    Trigger for Vellum-managed integration events.

    VellumIntegrationTrigger uses an inheritance pattern with Schema to define typed
    trigger attributes. Subclasses must specify provider, integration_name, slug,
    and trigger_nano_id, along with a Schema inner class defining available attributes.

    Examples:
        Define a trigger class with Schema:
            >>> class SlackNewMessage(VellumIntegrationTrigger):
            ...     provider = "COMPOSIO"
            ...     integration_name = "SLACK"
            ...     slug = "slack_new_message"
            ...     trigger_nano_id = "abc123def456"
            ...
            ...     class Schema:
            ...         message: str
            ...         channel: str
            ...         user: str

        Use in workflow graph:
            >>> class MyWorkflow(BaseWorkflow):
            ...     graph = SlackNewMessage >> ProcessMessageNode

        Reference trigger attributes in nodes:
            >>> class ProcessNode(BaseNode):
            ...     class Outputs(BaseNode.Outputs):
            ...         text = SlackNewMessage.message
            ...         channel = SlackNewMessage.channel

        Instantiate for testing:
            >>> trigger = SlackNewMessage(event_data={
            ...     "message": "Hello world",
            ...     "channel": "C123456",
            ...     "user": "U789"
            ... })
            >>> trigger.message
            'Hello world'

    Note:
        Generates a deterministic __id__ field (like BaseNode/BaseWorkflow) for
        UUID generation and serialization based on provider|integration_name|slug.
    """

    # Class variables that identify this trigger (must be overridden in subclasses)
    provider: ClassVar[Optional[VellumIntegrationProviderType]] = None
    integration_name: ClassVar[Optional[str]] = None
    slug: ClassVar[Optional[str]] = None
    trigger_nano_id: ClassVar[Optional[str]] = None
    attributes: ClassVar[Optional[Dict[str, Any]]] = None

    def __init_subclass__(cls, **kwargs):
        """
        Process subclasses to support inheritance pattern with Schema.

        This method is called when a class inherits from VellumIntegrationTrigger.
        It generates the __id__ field and processes the Schema inner class if present.
        """
        super().__init_subclass__(**kwargs)

        # Generate __id__ field if we have the required attributes (like BaseNode does)
        if cls.provider and cls.integration_name and cls.slug:
            # Convert string provider to enum if needed
            if isinstance(cls.provider, str):
                cls.provider = VellumIntegrationProviderType(cls.provider)

            # Generate deterministic ID using semantic identity
            trigger_identity = f"{cls.provider.value}|{cls.integration_name}|{cls.slug}"
            cls.__id__ = uuid4_from_hash(trigger_identity)

            # Initialize attributes if not set
            if cls.attributes is None:
                cls.attributes = {}

            # Initialize cache attributes
            if not hasattr(cls, "__trigger_attribute_ids__"):
                cls.__trigger_attribute_ids__ = {}
            if not hasattr(cls, "__trigger_attribute_cache__"):
                cls.__trigger_attribute_cache__ = {}

            # Process Schema if defined
            if hasattr(cls, "Schema"):
                cls._process_schema()

    @classmethod
    def _process_schema(cls):
        """
        Process the Schema inner class to create TriggerAttributeReferences.

        This method converts attributes defined in the Schema class into
        TriggerAttributeReference objects that can be used in workflow definitions.
        """
        schema = cls.Schema

        # Reserved class variable names that should not be overwritten by Schema attributes
        reserved_names = {"provider", "integration_name", "slug", "trigger_nano_id", "attributes"}

        # Get all attributes from Schema (both annotated and regular attributes)
        schema_attrs = set()

        # Process type annotations if available
        if hasattr(schema, "__annotations__"):
            schema_attrs.update(schema.__annotations__.keys())

        # Process regular attributes
        for attr_name in dir(schema):
            if not attr_name.startswith("_"):
                schema_attrs.add(attr_name)

        # Create TriggerAttributeReference for each schema attribute
        for attr_name in schema_attrs:
            # Skip reserved class variable names to avoid conflicts
            if attr_name in reserved_names:
                continue

            # Get type hint if available
            attr_type = object
            if hasattr(schema, "__annotations__") and attr_name in schema.__annotations__:
                attr_type = schema.__annotations__[attr_name]

            # Generate deterministic ID for this attribute
            trigger_identity = f"{cls.provider.value}|{cls.integration_name}|{cls.slug}"
            attribute_id = uuid4_from_hash(f"{trigger_identity}|{attr_name}")
            cls.__trigger_attribute_ids__[attr_name] = attribute_id

            # Create and cache the reference
            reference = TriggerAttributeReference(
                name=attr_name,
                types=(attr_type,) if attr_type != object else (object,),
                instance=None,
                trigger_class=cls,
            )
            cls.__trigger_attribute_cache__[attr_name] = reference

            # Add as class attribute for direct access
            setattr(cls, attr_name, reference)

    def __init__(self, event_data: dict):
        """
        Initialize trigger with event data from the integration.

        The trigger dynamically populates its attributes based on the event_data
        dictionary keys. Any key in event_data becomes an accessible attribute.

        Args:
            event_data: Raw event data from the integration. Keys become trigger attributes.

        Examples:
            >>> class SlackMessage(VellumIntegrationTrigger):
            ...     provider = "COMPOSIO"
            ...     integration_name = "SLACK"
            ...     slug = "slack_new_message"
            ...     trigger_nano_id = "abc123"
            ...     class Schema:
            ...         message: str
            ...         channel: str
            >>> trigger = SlackMessage(event_data={
            ...     "message": "Hello",
            ...     "channel": "C123"
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
    def get_trigger_id(cls) -> "UUID":
        """
        Get the deterministic UUID for this trigger.

        The trigger ID is generated from the semantic identity (provider|integration|slug)
        and is set during __init_subclass__ as the __id__ field.

        Returns:
            UUID: The deterministic trigger ID

        Raises:
            AttributeError: If called on base VellumIntegrationTrigger without configuration

        Examples:
            >>> class SlackMessage(VellumIntegrationTrigger):
            ...     provider = "COMPOSIO"
            ...     integration_name = "SLACK"
            ...     slug = "slack_new_message"
            ...     trigger_nano_id = "abc123"
            ...     class Schema:
            ...         message: str
            >>> trigger_id = SlackMessage.get_trigger_id()
        """
        if not hasattr(cls, "__id__"):
            raise AttributeError(
                "get_trigger_id() requires a configured trigger class. "
                "Inherit from VellumIntegrationTrigger and set provider, integration_name, "
                "and slug class variables."
            )

        return cls.__id__

    @classmethod
    def to_exec_config(cls) -> ComposioIntegrationTriggerExecConfig:
        """
        Generate execution configuration for serialization.

        This method creates a ComposioIntegrationTriggerExecConfig from the trigger
        class's configuration, which is used during serialization to the backend.

        Returns:
            ComposioIntegrationTriggerExecConfig with all required fields

        Raises:
            AttributeError: If called on base VellumIntegrationTrigger without configuration

        Examples:
            >>> class SlackMessage(VellumIntegrationTrigger):
            ...     provider = "COMPOSIO"
            ...     integration_name = "SLACK"
            ...     slug = "slack_new_message"
            ...     trigger_nano_id = "abc123"
            ...     class Schema:
            ...         message: str
            >>> exec_config = SlackMessage.to_exec_config()
            >>> exec_config.slug
            'slack_new_message'
        """
        if not hasattr(cls, "slug") or cls.slug is None:
            raise AttributeError(
                "to_exec_config() requires a configured trigger class. "
                "Inherit from VellumIntegrationTrigger and set provider, integration_name, "
                "slug, and trigger_nano_id class variables."
            )

        # Ensure provider is an enum (for inheritance pattern where it might be a string)
        provider = cls.provider
        if isinstance(provider, str):
            provider = VellumIntegrationProviderType(provider)

        return ComposioIntegrationTriggerExecConfig(
            provider=provider,
            integration_name=cls.integration_name,
            slug=cls.slug,
            trigger_nano_id=cls.trigger_nano_id,
            attributes=cls.attributes or {},
        )
