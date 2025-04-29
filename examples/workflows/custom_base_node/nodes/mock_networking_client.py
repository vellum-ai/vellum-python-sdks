import json

from utils.networking import MyCustomNetworkingClient

from vellum import (
    ChatMessage,
    FunctionCall,
    FunctionCallChatMessageContent,
    FunctionCallChatMessageContentValue,
    StringChatMessageContent,
)
from vellum.workflows.nodes.bases import BaseNode

from ..state import State


class MockNetworkingClient(BaseNode[State]):
    """
    A base node for which you can that mimics a networking call.

    Adapt this implementation to handle your own use cases surrounding:
    - HTTP
    - gRPC
    - GraphQL
    - Web Scraping
    - Database
    - and more!
    """

    action: FunctionCall

    class Outputs(BaseNode.Outputs):
        response: dict

    def run(self) -> BaseNode.Outputs:
        self.state.chat_history.append(
            ChatMessage(
                role="ASSISTANT",
                content=FunctionCallChatMessageContent(
                    value=FunctionCallChatMessageContentValue.model_validate(self.action.model_dump())
                ),
            )
        )

        client = MyCustomNetworkingClient()
        response = client.invoke_request(name=self.action.name, request=self.action.arguments)

        self.state.chat_history.append(
            ChatMessage(
                role="FUNCTION",
                content=StringChatMessageContent(value=json.dumps(response)),
                source=self.action.id,
            )
        )

        return self.Outputs(response=response)
