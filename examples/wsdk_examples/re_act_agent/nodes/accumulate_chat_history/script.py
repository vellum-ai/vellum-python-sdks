import json


def main(
    invoked_functions,
    assistant_message,
    current_chat_history,
) -> list:
    result = [*current_chat_history, {"role": "ASSISTANT", "content": {"type": "ARRAY", "value": assistant_message}}]

    for fn in invoked_functions:
        fn_result = {
            "role": "FUNCTION",
            "content": {"type": "STRING", "value": json.dumps(fn["value"]["function_result"])},
            "source": fn["value"]["function_context"]["tool_id"],
        }
        result.append(fn_result)

    return result
