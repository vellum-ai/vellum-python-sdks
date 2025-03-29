def main(
    current_chat_history,
    assistant_message,
) -> int:
    return [
        *current_chat_history,
        {
            "role": "ASSISTANT",
            "content": assistant_message[0],
        },
    ]
