from vellum.workflows.nodes.displayable import InlinePromptNode


class PromptNode(InlinePromptNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        {
            "block_type": "CHAT_MESSAGE",
            "chat_role": "USER",
            "chat_message_unterminated": False,
            "chat_message": (
                "Answer the following query: {{ inputs.query }}\n\n"
                "Context: {{ inputs.context or 'No context provided' }}"
            ),
        }
    ]
