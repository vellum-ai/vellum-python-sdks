from vellum import ArrayChatMessageContent, ChatMessage, ImageChatMessageContent, StringChatMessageContent, VellumImage
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
                    text="https://storage.googleapis.com/vellum-public/help-docs/extract-from-image-of-receipt.jpeg",
                    content=ArrayChatMessageContent(
                        value=[
                            ImageChatMessageContent(
                                value=VellumImage(
                                    src="https://storage.googleapis.com/vellum-public/help-docs/extract-from-image-of-receipt.jpeg",
                                    metadata={
                                        "detail": "low",
                                    },
                                ),
                            ),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text='\n{\n  "provider_name": "WAL-MART",\n  "provider_address": "",\n  "provider_phone": "(515) 986-1783",\n  "date": "08/20/10",\n  "items_in_receipt": [\n    {\n      "name": "BANANAS",\n      "price": 0.20\n    },\n    {\n      "name": "FRAP",\n      "price": 5.48\n    }\n  ],\n  "number_of_items": 2,\n  "payment_total": 5.11\n}',
                    content=StringChatMessageContent(
                        value='\n{\n  "provider_name": "WAL-MART",\n  "provider_address": "",\n  "provider_phone": "(515) 986-1783",\n  "date": "08/20/10",\n  "items_in_receipt": [\n    {\n      "name": "BANANAS",\n      "price": 0.20\n    },\n    {\n      "name": "FRAP",\n      "price": 5.48\n    }\n  ],\n  "number_of_items": 2,\n  "payment_total": 5.11\n}'
                    ),
                ),
            ]
        ),
    ],
)

runner.run()
