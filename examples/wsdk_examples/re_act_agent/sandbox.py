from vellum import ArrayChatMessageContent, ChatMessage, StringChatMessageContent
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .inputs import Inputs
from .workflow import Workflow

if __name__ != "__main__":
    raise Exception("This file is not meant to be imported")


runner = WorkflowSandboxRunner(
    workflow=Workflow(),
    inputs=[
        Inputs(
            chat_history=[
                ChatMessage(
                    role="USER",
                    text="Can you compare the price and ratings of the top home air conditioning / mini-split products?",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(
                                value="Can you compare the price and ratings of the top home air conditioning / mini-split products?"
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ],
)

runner.run()
