from vellum import ChatMessagePromptBlock, PlainTextPromptBlock, RichTextPromptBlock


def SystemMessage(content: str) -> ChatMessagePromptBlock:
    """
    Create a system message that autocasts to ChatMessagePromptBlock.

    Args:
        content: The text content for the system message

    Returns:
        ChatMessagePromptBlock configured as a system message
    """
    return ChatMessagePromptBlock(
        chat_role="SYSTEM", blocks=[RichTextPromptBlock(blocks=[PlainTextPromptBlock(text=content)])]
    )


def UserMessage(content: str) -> ChatMessagePromptBlock:
    """
    Create a user message that autocasts to ChatMessagePromptBlock.

    Args:
        content: The text content for the user message

    Returns:
        ChatMessagePromptBlock configured as a user message
    """
    return ChatMessagePromptBlock(
        chat_role="USER", blocks=[RichTextPromptBlock(blocks=[PlainTextPromptBlock(text=content)])]
    )
