from vellum import (
    ArrayChatMessageContent,
    ChatMessage,
    DocumentChatMessageContent,
    StringChatMessageContent,
    VellumDocument,
)
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .inputs import Inputs
from .workflow import Workflow

if __name__ != "__main__":
    raise Exception("This file is not meant to be imported")


runner = WorkflowSandboxRunner(
    workflow=Workflow(),
    inputs=[
        Inputs(
            image_url="https://storage.googleapis.com/vellum-public/onboarding-assets/5924_png.rf.b3609806540c821c7a51bba3bf0b1f09.pdf",
            workflow_input_chat_history=[
                ChatMessage(
                    role="USER",
                    text="vellum:uploaded-file:0e48b359-2677-4133-b4a5-7ab59f5f9369",
                    content=ArrayChatMessageContent(
                        value=[
                            DocumentChatMessageContent(
                                value=VellumDocument(
                                    src="vellum:uploaded-file:0e48b359-2677-4133-b4a5-7ab59f5f9369",
                                    metadata={
                                        "id": "0e48b359-2677-4133-b4a5-7ab59f5f9369",
                                        "type": "DOCUMENT",
                                        "detail": "high",
                                        "expiry": "2025-04-01T05:51:12.000Z",
                                        "signedUrl": "https://storage.googleapis.com/vellum-django/uploaded-files/55b14aa3-55ea-4785-83fb-dede9e01babc/f6b086c6-c2c9-4cf5-a6f1-2ea8e46fead2/0e48b359-2677-4133-b4a5-7ab59f5f9369/5924_png.rf.b3609806540c821c7a51bba3bf0b1f09.pdf?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=585775334980-compute%40developer.gserviceaccount.com%2F20250324%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20250324T235113Z&X-Goog-Expires=604799&X-Goog-SignedHeaders=host&X-Goog-Signature=8bfb4a557f54f46c804ff6518d6868036e47662213dd9afb4a8f1e34f599a967183f76c422dbb26e719b6302f844e18a0528cfe27a4ccb0a76aa04ba4468ebbe5aafebda518d5f9dd7f597fb308c5012af313c115aa4c8b173e283473900f38500df8141c021ca1e7d25c0883ea4732867138e355875470cf6e82708693af42f364f4f4ad2c754f3f40b7a9cdfe2b7511c3eb7c123d73709cf6eb9e011b6e70e10d4850eae997d7a61792c4eb2272a503505520e17a5ca06843f1bd17c4c935fe625e520053289a4d05a1f11277c32550f783cc35f344dfe3c12276ef9d93b33ec818cd29cd6d75ce9dc8b1fe2412381b4a964d3c0d46e2661f260d383d6adac",
                                    },
                                ),
                            ),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text='Based on the Model Selection Chart provided, I can see that for a 1.5" valve, the large top pressure rating is 500 psi (34.0 bar). This applies to both the 2WNC and 2WNO configurations shown in the chart for the 1.5" basic valve size.',
                    content=StringChatMessageContent(
                        value='Based on the Model Selection Chart provided, I can see that for a 1.5" valve, the large top pressure rating is 500 psi (34.0 bar). This applies to both the 2WNC and 2WNO configurations shown in the chart for the 1.5" basic valve size.'
                    ),
                ),
            ],
        ),
    ],
)

runner.run()
