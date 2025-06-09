from typing import Optional

from vellum.workflows.references import EnvironmentVariableReference


class Environment:
    @staticmethod
    def get(name: str, default: Optional[str] = "") -> EnvironmentVariableReference:
        return EnvironmentVariableReference(name=name, default=default)
