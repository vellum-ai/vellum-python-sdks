from vellum import ChatMessagePromptBlock, PlainTextPromptBlock, RichTextPromptBlock


def BasicSystemMessage(content: str) -> ChatMessagePromptBlock:
    """
    Create a basic system message that autocasts to ChatMessagePromptBlock.

    Args:
        content: The text content for the system message

    Returns:
        ChatMessagePromptBlock configured as a system message
    """
    return ChatMessagePromptBlock(
        chat_role="SYSTEM", blocks=[RichTextPromptBlock(blocks=[PlainTextPromptBlock(text=content)])]
    )


def BasicUserMessage(content: str) -> ChatMessagePromptBlock:
    """
    Create a basic user message that autocasts to ChatMessagePromptBlock.

    Args:
        content: The text content for the user message

    Returns:
        ChatMessagePromptBlock configured as a user message
    """
    return ChatMessagePromptBlock(
        chat_role="USER", blocks=[RichTextPromptBlock(blocks=[PlainTextPromptBlock(text=content)])]
    )
