import json
from typing import Union


def is_valid_json_string(value: Union[str, bytes]) -> bool:
    """Determines whether the given value is a valid JSON string."""

    try:
        json.loads(value)
    except ValueError:
        return False
    return True
