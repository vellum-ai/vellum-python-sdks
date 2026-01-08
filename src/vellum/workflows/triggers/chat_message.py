from typing import TYPE_CHECKING, Any, List, Optional, Union

from vellum.client.types import ArrayChatMessageContent, ArrayChatMessageContentItem, ChatMessage, ChatMessageContent
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.references.output import OutputReference
from vellum.workflows.triggers.base import BaseTrigger

if TYPE_CHECKING:
    from vellum.workflows.state.base import BaseState


class ChatMessageTrigger(BaseTrigger):
    """
    Trigger for chat-based workflows that supports multi-turn conversations.

    Appends user message to state.chat_history at workflow start, and assistant
    response after workflow completion. Use previous_execution_id to maintain
    conversation state across executions.

    Attributes:
        message: The incoming chat message content.
    """

    message: List[ArrayChatMessageContentItem]

    class Config(BaseTrigger.Config):
        output: Optional[BaseDescriptor[Any]] = None

    def __on_workflow_initiated__(self, state: "BaseState") -> None:
        """Appends user message to state.chat_history at workflow start."""
        if not hasattr(state, "chat_history"):
            return

        user_message = ChatMessage(
            role="USER",
            content=ArrayChatMessageContent(value=self.message),
        )
        state.chat_history.append(user_message)

    def __on_workflow_fulfilled__(self, state: "BaseState") -> None:
        """Appends assistant response to state.chat_history after workflow completion."""
        if not hasattr(state, "chat_history"):
            return

        output = self.Config.output
        if output is not None:
            resolved_output = self._resolve_output(output, state)
            assistant_message = ChatMessage(
                role="ASSISTANT",
                content=resolved_output if not isinstance(resolved_output, str) else None,
                text=resolved_output if isinstance(resolved_output, str) else None,
            )
            state.chat_history.append(assistant_message)

    def _resolve_output(
        self,
        output: BaseDescriptor[Any],
        state: "BaseState",
    ) -> Union[str, ChatMessageContent]:
        """Resolves output reference, handling workflow output references."""
        descriptor = output
        if isinstance(output, LazyReference) and callable(output._get):
            descriptor = output._get()

        if isinstance(descriptor, OutputReference) and isinstance(descriptor.instance, BaseDescriptor):
            return resolve_value(descriptor.instance, state)

        return resolve_value(output, state)

    class Display(BaseTrigger.Display):
        label: str = "Chat Message"
        icon: Optional[str] = "vellum:icon:message-dots"
        color: Optional[str] = "blue"
