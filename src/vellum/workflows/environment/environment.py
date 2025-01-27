from typing import Union

from vellum.workflows.references import EnvironmentVariableReference


class Environment:
    @staticmethod
    def get(name: str, default: Union[str, None] = None) -> EnvironmentVariableReference:
        return EnvironmentVariableReference(name=name, default=default)
