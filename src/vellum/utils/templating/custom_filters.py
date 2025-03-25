import json
from typing import Any, Union

from jinja2 import Undefined
from jinja2.utils import htmlsafe_json_dumps

from vellum.workflows.state.encoder import DefaultStateEncoder


def is_valid_json_string(value: Union[str, bytes]) -> bool:
    """Determines whether the given value is a valid JSON string."""

    try:
        json.loads(value)
    except ValueError:
        return False
    return True


def replace(s: Any, old: Any, new: Any) -> str:
    def encode_to_str(obj: Any) -> str:
        """Encode an object for template rendering using DefaultStateEncoder."""
        try:
            if isinstance(obj, str):
                return obj
            return json.dumps(obj, cls=DefaultStateEncoder)
        except TypeError:
            return str(obj)

    if old == "":
        return encode_to_str(s)

    s_str = encode_to_str(s)
    old_str = encode_to_str(old)
    new_str = encode_to_str(new)
    return s_str.replace(old_str, new_str)


def safe_tojson(value: Any) -> str:
    if isinstance(value, Undefined):
        return ""
    return htmlsafe_json_dumps(value, cls=DefaultStateEncoder)
