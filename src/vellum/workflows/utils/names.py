import re


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
