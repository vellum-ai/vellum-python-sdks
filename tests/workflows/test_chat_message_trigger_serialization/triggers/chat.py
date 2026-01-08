from typing import Optional

from vellum.workflows.triggers.chat_message import ChatMessageTrigger


class Chat(ChatMessageTrigger):
    message: str

    class Config(ChatMessageTrigger.Config):
        output: Optional[str] = None

    class Display(ChatMessageTrigger.Display):
        label: str = "Chat"
