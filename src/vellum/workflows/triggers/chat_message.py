from typing import TYPE_CHECKING, Any, ClassVar, List, Optional, Union

from vellum.client.types import (
    ArrayChatMessageContent,
    ArrayChatMessageContentItem,
    AudioChatMessageContent,
    ChatMessage,
    ChatMessageContent,
    DocumentChatMessageContent,
    FunctionCallChatMessageContent,
    ImageChatMessageContent,
    StringChatMessageContent,
    VideoChatMessageContent,
)
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.references.output import OutputReference
from vellum.workflows.triggers.base import BaseTrigger
from vellum.workflows.utils.pydantic_schema import validate_obj_as

if TYPE_CHECKING:
    from vellum.workflows.state.base import BaseState


class ChatMessageTrigger(BaseTrigger):
    """
    Trigger for chat-based workflows that supports multi-turn conversations.

    Appends user message to state.chat_history at workflow start, and assistant
    response after workflow completion. Use previous_execution_id to maintain
    conversation state across executions.

    Attributes:
        message: The incoming chat message content. Can be a string or a list of content items.
    """

    message: Union[str, List[ArrayChatMessageContentItem]]

    class Config(BaseTrigger.Config):
        output: Optional[BaseDescriptor[Any]] = None

    def __init__(self, **kwargs: Any):
        """Initialize ChatMessageTrigger, converting VellumValue objects to ChatMessageContent if needed."""
        # Convert message from VellumValue format to ChatMessageContent format if needed
        if "message" in kwargs:
            message = kwargs["message"]
            # Handle string messages by converting to a list with a single StringChatMessageContent
            if isinstance(message, str):
                kwargs["message"] = [StringChatMessageContent(value=message)]
            elif isinstance(message, list):
                converted_message = []
                for item in message:
                    # If it's already a ChatMessageContent type, keep it as-is
                    if isinstance(
                        item,
                        (
                            StringChatMessageContent,
                            ImageChatMessageContent,
                            AudioChatMessageContent,
                            VideoChatMessageContent,
                            DocumentChatMessageContent,
                            FunctionCallChatMessageContent,
                        ),
                    ):
                        converted_message.append(item)
                    # Handle raw strings in the array by wrapping them in StringChatMessageContent
                    elif isinstance(item, str):
                        converted_message.append(StringChatMessageContent(value=item))
                    # Convert VellumValue objects or dicts to ChatMessageContent
                    # Use discriminated union validation
                    else:
                        # Get the dict representation (either from Pydantic model or already a dict)
                        item_dict = item.model_dump() if hasattr(item, "model_dump") else item
                        converted_message.append(
                            validate_obj_as(ArrayChatMessageContentItem, item_dict)  # type: ignore[arg-type]
                        )

                kwargs["message"] = converted_message

        super().__init__(**kwargs)

    def __on_workflow_initiated__(self, state: "BaseState") -> None:
        """Appends user message to state.chat_history at workflow start."""
        if not hasattr(state, "chat_history"):
            return

        if state.chat_history is None:
            state.chat_history = []

        if isinstance(self.message, str):
            user_message = ChatMessage(
                role="USER",
                text=self.message,
            )
        else:
            user_message = ChatMessage(
                role="USER",
                content=ArrayChatMessageContent(value=self.message),
            )
        state.chat_history.append(user_message)

    def __on_workflow_fulfilled__(self, state: "BaseState") -> None:
        """Appends assistant response to state.chat_history after workflow completion."""
        if not hasattr(state, "chat_history"):
            return

        if state.chat_history is None:
            state.chat_history = []

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

    __trigger_name__: ClassVar[str] = "chat"

    class Display(BaseTrigger.Display):
        label: str = "Chat Message"
        icon: Optional[str] = "vellum:icon:message-dots"
        color: Optional[str] = "blue"
