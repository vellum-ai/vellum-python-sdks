from abc import ABC
from typing import ClassVar, Optional

from vellum.workflows.triggers.base import BaseTrigger


class IntegrationTrigger(BaseTrigger, ABC):
    """
    Base class for integration-based triggers (Slack, Email, etc.).

    Integration triggers:
    - Are initiated by external events (webhooks, API calls)
    - Produce attributes that downstream nodes can reference
    - Require configuration (auth, webhooks, etc.)

    Examples:
        # Define an integration trigger
        class MyIntegrationTrigger(IntegrationTrigger):
            data: str

            @classmethod
            def process_event(cls, event_data: dict):
                trigger = cls()
                trigger.data = event_data.get("data", "")
                return trigger

        # Use in workflow
        class MyWorkflow(BaseWorkflow):
            graph = MyIntegrationTrigger >> ProcessNode

        # Reference trigger attributes in nodes
        class ProcessNode(BaseNode):
            class Outputs(BaseNode.Outputs):
                result = MyIntegrationTrigger.data

    Note:
        Unlike ManualTrigger, integration triggers provide structured attributes
        that downstream nodes can reference directly.
    """

    # Configuration that can be set at runtime
    config: ClassVar[Optional[dict]] = None

    @classmethod
    def process_event(cls, event_data: dict) -> "IntegrationTrigger":
        """
        Process incoming webhook/event data and return trigger instance.

        This method should be implemented by subclasses to parse external
        event payloads (e.g., Slack webhooks, email notifications) into
        a trigger instance with populated attributes.

        Args:
            event_data: Raw event data from the external system

        Returns:
            Trigger instance with attributes populated from parsed event data

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError(f"{cls.__name__} must implement process_event() method to handle external events")
