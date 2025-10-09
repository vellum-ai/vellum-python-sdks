from abc import ABC
from typing import ClassVar, Optional

from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.triggers.base import BaseTrigger


class IntegrationTrigger(BaseTrigger, ABC):
    """
    Base class for integration-based triggers (Slack, Email, etc.).

    Integration triggers:
    - Are initiated by external events (webhooks, API calls)
    - Produce outputs that downstream nodes can reference
    - Require configuration (auth, webhooks, etc.)

    Examples:
        # Define an integration trigger
        class MyIntegrationTrigger(IntegrationTrigger):
            class Outputs(IntegrationTrigger.Outputs):
                data: str

            @classmethod
            def process_event(cls, event_data: dict):
                return cls.Outputs(data=event_data.get("data", ""))

        # Use in workflow
        class MyWorkflow(BaseWorkflow):
            graph = MyIntegrationTrigger >> ProcessNode

    Note:
        Unlike ManualTrigger, integration triggers provide structured outputs
        that downstream nodes can reference directly via Outputs.
    """

    class Outputs(BaseOutputs):
        """Base outputs for integration triggers."""

        pass

    # Configuration that can be set at runtime
    config: ClassVar[Optional[dict]] = None

    @classmethod
    def process_event(cls, event_data: dict) -> "IntegrationTrigger.Outputs":
        """
        Process incoming webhook/event data and return trigger outputs.

        This method should be implemented by subclasses to parse external
        event payloads (e.g., Slack webhooks, email notifications) into
        structured trigger outputs.

        Args:
            event_data: Raw event data from the external system

        Returns:
            Trigger outputs containing parsed event data

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError(f"{cls.__name__} must implement process_event() method to handle external events")
