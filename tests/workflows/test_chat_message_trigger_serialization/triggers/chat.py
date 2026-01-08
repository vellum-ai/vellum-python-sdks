from vellum.workflows.triggers.chat_message import ChatMessageTrigger


class Chat(ChatMessageTrigger):
    class Display(ChatMessageTrigger.Display):
        label: str = "Chat"
