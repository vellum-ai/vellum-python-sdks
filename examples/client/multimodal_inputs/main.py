import os

from vellum import (
    ArrayChatMessageContent,
    ChatHistoryInput,
    ChatMessage,
    DocumentChatMessageContent,
    ImageChatMessageContent,
    StringChatMessageContent,
    Vellum,
    VellumDocument,
    VellumImage,
)

client = Vellum(api_key=os.environ["VELLUM_API_KEY"])

# PDF Example
pdf_link = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
response = client.execute_prompt(
    prompt_deployment_name="pdfs-example-prompt",
    inputs=[
        ChatHistoryInput(
            name="chat_history",
            value=[
                ChatMessage(
                    role="USER",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="What's in the PDF?"),
                            DocumentChatMessageContent(value=VellumDocument(src=pdf_link)),
                        ]
                    ),
                )
            ],
        ),
    ],
)
print(response.outputs[0].value)

# Image Example
image_link = "https://fastly.picsum.photos/id/53/200/300.jpg?hmac=KbEX4oNyVO15M-9S4xMsefrElB1uiO3BqnvVqPnhPgE"
response = client.execute_prompt(
    prompt_deployment_name="pdfs-example-prompt",
    inputs=[
        ChatHistoryInput(
            name="chat_history",
            value=[
                ChatMessage(
                    role="USER",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="What's in the image?"),
                            ImageChatMessageContent(value=VellumImage(src=image_link)),
                        ]
                    ),
                )
            ],
        ),
    ],
)
print(response.outputs[0].value)
