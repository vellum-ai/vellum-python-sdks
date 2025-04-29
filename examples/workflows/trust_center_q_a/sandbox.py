from vellum import ChatMessage, StringChatMessageContent
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
                    text="How often is employee training?",
                    content=StringChatMessageContent(value="How often is employee training?"),
                ),
            ]
        ),
        Inputs(
            chat_history=[
                ChatMessage(
                    role="USER",
                    text="How often is employee training?",
                    content=StringChatMessageContent(value="How often is employee training?"),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="Employee training, as outlined in the provided policies, occurs on an annual basis. All new hires are required to complete information security awareness training as part of their onboarding process and then annually thereafter. This ongoing training includes security and privacy requirements, the correct use of information assets and facilities, and, consistent with assigned roles and responsibilities, incident response and contingency training. Additionally, individuals responsible for supporting or writing code for internet-facing applications or internal applications that handle customer information must complete annual security training specific to secure coding practices, which includes OWASP secure development principles and awareness of the OWASP top 10 vulnerabilities for the most recent year available.\n\nCitation: Policy Information Security Policy - v1.pdf & Policy Software Development Life Cycle Policy - v1.pdf.",
                    content=StringChatMessageContent(
                        value="Employee training, as outlined in the provided policies, occurs on an annual basis. All new hires are required to complete information security awareness training as part of their onboarding process and then annually thereafter. This ongoing training includes security and privacy requirements, the correct use of information assets and facilities, and, consistent with assigned roles and responsibilities, incident response and contingency training. Additionally, individuals responsible for supporting or writing code for internet-facing applications or internal applications that handle customer information must complete annual security training specific to secure coding practices, which includes OWASP secure development principles and awareness of the OWASP top 10 vulnerabilities for the most recent year available.\n\nCitation: Policy Information Security Policy - v1.pdf & Policy Software Development Life Cycle Policy - v1.pdf."
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="How does the organization do device management?",
                    content=StringChatMessageContent(value="How does the organization do device management?"),
                ),
            ]
        ),
        Inputs(
            chat_history=[
                ChatMessage(
                    role="USER",
                    text="How often is employee training?",
                    content=StringChatMessageContent(value="How often is employee training?"),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="Employee training, as outlined in the provided policies, occurs on an annual basis. All new hires are required to complete information security awareness training as part of their onboarding process and then annually thereafter. This ongoing training includes security and privacy requirements, the correct use of information assets and facilities, and, consistent with assigned roles and responsibilities, incident response and contingency training. Additionally, individuals responsible for supporting or writing code for internet-facing applications or internal applications that handle customer information must complete annual security training specific to secure coding practices, which includes OWASP secure development principles and awareness of the OWASP top 10 vulnerabilities for the most recent year available.\n\nCitation: Policy Information Security Policy - v1.pdf & Policy Software Development Life Cycle Policy - v1.pdf.",
                    content=StringChatMessageContent(
                        value="Employee training, as outlined in the provided policies, occurs on an annual basis. All new hires are required to complete information security awareness training as part of their onboarding process and then annually thereafter. This ongoing training includes security and privacy requirements, the correct use of information assets and facilities, and, consistent with assigned roles and responsibilities, incident response and contingency training. Additionally, individuals responsible for supporting or writing code for internet-facing applications or internal applications that handle customer information must complete annual security training specific to secure coding practices, which includes OWASP secure development principles and awareness of the OWASP top 10 vulnerabilities for the most recent year available.\n\nCitation: Policy Information Security Policy - v1.pdf & Policy Software Development Life Cycle Policy - v1.pdf."
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="How does the organization do device management?",
                    content=StringChatMessageContent(value="How does the organization do device management?"),
                ),
            ]
        ),
    ],
)

runner.run()
