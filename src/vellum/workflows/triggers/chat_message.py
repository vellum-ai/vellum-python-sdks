from typing import TYPE_CHECKING, Any, ClassVar, Optional, Union

from vellum.client.types import ChatMessage, ChatMessageContent
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.references.output import OutputReference
from vellum.workflows.triggers.base import BaseTrigger

if TYPE_CHECKING:
    from vellum.workflows.outputs import BaseOutputs
    from vellum.workflows.state.base import BaseState


class ChatMessageTrigger(BaseTrigger):
    """
    Trigger for chat-based workflows that supports multi-turn conversations.

    Automatically appends user message and assistant response to state.chat_history
    after workflow completion. Use previous_execution_id to maintain conversation state.

    Attributes:
        message: The incoming chat message (text string or multi-modal content).
        output: Class-level reference to a workflow output to append as assistant
            response. Use LazyReference for forward references:
            `output = LazyReference(lambda: MyWorkflow.Outputs.response)`
    """

    message: Union[str, ChatMessageContent]
    output: ClassVar[Optional[BaseDescriptor[Any]]] = None

    def __on_workflow_fulfilled__(self, state: "BaseState", outputs: "BaseOutputs") -> None:
        """Appends user message and assistant response to state.chat_history."""
        if not hasattr(state, "chat_history"):
            return

        user_message = ChatMessage(
            role="USER",
            content=self.message if not isinstance(self.message, str) else None,
            text=self.message if isinstance(self.message, str) else None,
        )
        state.chat_history.append(user_message)

        if self.output is not None:
            resolved_output = self._resolve_output(self.output, state, outputs)
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
        outputs: "BaseOutputs",
    ) -> Union[str, ChatMessageContent]:
        """Resolves output reference from workflow outputs or state."""
        descriptor = output
        if isinstance(output, LazyReference) and callable(output._get):
            descriptor = output._get()

        if isinstance(descriptor, OutputReference) and hasattr(outputs, descriptor.name):
            return getattr(outputs, descriptor.name)
        return resolve_value(output, state)

    class Display(BaseTrigger.Display):
        label: str = "Chat Message"
        icon: Optional[str] = "vellum:icon:message"
        color: Optional[str] = "blue"
