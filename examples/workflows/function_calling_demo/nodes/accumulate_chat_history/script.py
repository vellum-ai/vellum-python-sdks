import json


def main(
    tool_id,
    function_result,
    assistant_message,
    current_chat_history,
) -> int:
    return [
        *current_chat_history,
        {
            "role": "ASSISTANT",
            "content": assistant_message[0],
        },
        {
            "role": "FUNCTION",
            "content": {
              "type": "STRING",
              "value": json.dumps(function_result)
            },
            "source": tool_id
        }
    ]
    