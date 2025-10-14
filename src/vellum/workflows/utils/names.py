import re
from typing import Optional

from pydash import snake_case


def pascal_to_title_case(pascal_str: str) -> str:
    title_case_str = re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", pascal_str)

    words = title_case_str.split()
    result_words = []

    for word in words:
        if word.isupper():
            result_words.append(word)
        # Otherwise, apply title case
        else:
            result_words.append(word.capitalize())

    return " ".join(result_words)


def snake_to_title_case(snake_str: str) -> str:
    return pascal_to_title_case(snake_str.replace("_", " "))


def create_module_name(*, deployment_name: Optional[str] = None, label: Optional[str] = None) -> Optional[str]:
    """Create a module name from deployment_name or label.

    Args:
        deployment_name: Optional deployment name to convert to snake_case
        label: Optional label to convert to snake_case (fallback if deployment_name not provided)

    Returns:
        Module name in snake_case format, or None if neither parameter is provided
    """
    if deployment_name:
        return snake_case(deployment_name)
    elif label:
        return snake_case(label)
    return None
