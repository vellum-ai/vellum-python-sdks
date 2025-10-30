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

            def __init__(self, **kwargs: Any):
                super().__init__(**kwargs)
                self.data = kwargs.get("data", "")

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
