from typing import Optional

from vellum.workflows.references import EnvironmentVariableReference


class EnvironmentVariables:
    @staticmethod
    def get(name: str, default: Optional[str] = None) -> EnvironmentVariableReference:
        return EnvironmentVariableReference(name=name, default=default)


Environment = EnvironmentVariables
