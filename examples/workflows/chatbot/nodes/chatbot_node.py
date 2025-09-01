from typing import Iterator

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.outputs import BaseOutput

from ..inputs import Inputs
from ..state import State


class ChatbotNode(BaseNode[State]):
    """A simple chatbot node that only manages state - stores user messages without prompt processing."""

    user_message = Inputs.user_message
    conversation_history = State.conversation_history
    message_count = State.message_count

    class Outputs(BaseNode.Outputs):
        conversation_history: list

    def run(self) -> Iterator[BaseOutput]:
        """Run the node and store user message in state."""
        # Get the user message from the input attribute
        user_message = self.user_message

        if not self.conversation_history:
            self.conversation_history = []

        if not self.message_count:
            self.message_count = 0

        # Update the state with the new message
        if self.state:

            # Add new user message to history
            self.conversation_history.append(f"User: {user_message}")

            # Update state
            self.state.conversation_history = self.conversation_history
            self.state.message_count = self.message_count + 1

        # Return the conversation history
        yield BaseOutput(name="conversation_history", value=self.conversation_history)
