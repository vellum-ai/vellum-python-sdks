import os
from typing import Union


def get_project_root() -> str:
    current_dir = os.getcwd()
    while current_dir != '/':
        if ".git" in os.listdir(current_dir):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    raise FileNotFoundError("Project root not found.")

def read_file_from_path(filepath: str) -> Union[str, None]:
    project_root = get_project_root()
    relative_filepath = os.path.join(project_root, filepath)

    if not os.path.exists(relative_filepath):
        return None

    with open(relative_filepath, 'r') as file:
        return file.read()
