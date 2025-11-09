from vellum import ArrayChatMessageContent, ChatMessage, ImageChatMessageContent, VellumImage
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .inputs import Inputs
from .workflow import Workflow

if __name__ != "__main__":
    raise Exception("This file is not meant to be imported")


runner = WorkflowSandboxRunner(
    workflow=Workflow(),
    inputs=[
        Inputs(
            image_url="https://picsum.photos/id/296/200/300",
            workflow_input_chat_history=[
                ChatMessage(
                    role="USER",
                    text="https://picsum.photos/id/296/200/300",
                    content=ArrayChatMessageContent(
                        value=[
                            ImageChatMessageContent(
                                value=VellumImage(
                                    src="https://picsum.photos/id/296/200/300",
                                    metadata={
                                        "detail": "high",
                                    },
                                ),
                            ),
                        ]
                    ),
                ),
            ],
        ),
        Inputs(
            image_url="https://picsum.photos/id/419/200/300",
            workflow_input_chat_history=[
                ChatMessage(
                    role="USER",
                    text="https://picsum.photos/id/419/200/300",
                    content=ArrayChatMessageContent(
                        value=[
                            ImageChatMessageContent(
                                value=VellumImage(
                                    src="https://picsum.photos/id/419/200/300",
                                    metadata={
                                        "detail": "high",
                                    },
                                ),
                            ),
                        ]
                    ),
                ),
            ],
        ),
    ],
)

runner.run()
