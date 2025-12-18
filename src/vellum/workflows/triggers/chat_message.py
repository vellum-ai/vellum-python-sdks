from typing import TYPE_CHECKING, Optional, Union

from vellum.client.types import ChatMessage, ChatMessageContent
from vellum.workflows.triggers.base import BaseTrigger

if TYPE_CHECKING:
    from vellum.workflows.outputs import BaseOutputs
    from vellum.workflows.state.base import BaseState


class ChatMessageTrigger(BaseTrigger):
    """
    Trigger for chat-based workflows that supports multi-turn conversations.

    This trigger is designed for conversational AI workflows where each incoming
    message triggers a new workflow execution. It supports multi-modal messages
    (text, images, video, audio, documents) and automatically manages chat history
    state when the workflow completes successfully.

    Attributes:
        message: The incoming chat message - can be a text string or multi-modal
            content (image, video, audio, document).
        output: Optional reference to node output to append as assistant response.
            Supports text strings or multi-modal content. If None, no assistant
            message is appended.

    Automatic State Management:
        When using ChatMessageTrigger, the framework automatically appends BOTH
        the user message and assistant response to state.chat_history AFTER the
        workflow completes successfully. This ensures atomic updates and prevents
        failed workflows from polluting chat history.

    Multi-turn Conversations:
        Use the existing previous_execution_id parameter to maintain conversation
        state across multiple message exchanges.

    Example:
        ```python
        class MyChatWorkflow(BaseWorkflow):
            graph = ChatMessageTrigger >> PromptNode

        # First message
        result = workflow.run(trigger=ChatMessageTrigger(message="Hello"))
        execution_id = result.span_id

        # Second message - loads previous state
        result = workflow.run(
            trigger=ChatMessageTrigger(message="How are you?"),
            previous_execution_id=execution_id
        )
        ```
    """

    message: Union[str, ChatMessageContent]
    output: Optional[Union[str, ChatMessageContent]] = None

    def __on_workflow_fulfilled__(self, state: "BaseState", outputs: "BaseOutputs") -> None:
        """
        Lifecycle hook called after workflow execution completes successfully.

        Automatically appends both user message and assistant response to chat_history.
        The assistant response is determined by the `output` attribute.

        This approach ensures atomic updates - both messages are added together after
        the workflow completes successfully.
        """
        if not hasattr(state, "chat_history"):
            return

        user_message = ChatMessage(
            role="USER",
            content=self.message if not isinstance(self.message, str) else None,
            text=self.message if isinstance(self.message, str) else None,
        )
        state.chat_history.append(user_message)

        if self.output is not None:
            assistant_message = ChatMessage(
                role="ASSISTANT",
                content=self.output if not isinstance(self.output, str) else None,
                text=self.output if isinstance(self.output, str) else None,
            )
            state.chat_history.append(assistant_message)

    class Display(BaseTrigger.Display):
        label: str = "Chat Message"
        icon: Optional[str] = "vellum:icon:message"
        color: Optional[str] = "blue"
